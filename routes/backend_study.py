import os, json, re
from flask import jsonify, request, Blueprint
from flask_cors import CORS
from pymongo import MongoClient
from pymongo import ReturnDocument
from dotenv import load_dotenv
from bson import ObjectId, errors
from flask_jwt_extended import get_jwt_identity, jwt_required
import certifi
from google import genai

load_dotenv()

study_bp = Blueprint("study_fc", __name__)
CORS(study_bp)

#get database credentials
db_user = os.getenv("DB_USERNAME")
db_pass = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")

google_api_key = os.getenv("GENAI_API_KEY")
ai_client = genai.Client(api_key=google_api_key) 


#database    
uri = f"mongodb+srv://{db_user}:{db_pass}@cognidy-cluster.oq1fqvx.mongodb.net/?retryWrites=true&w=majority&appName=cognidy-cluster" 
client = MongoClient(uri, tlsCAFile=certifi.where()) 

db = client[db_name]

@study_bp.route("/ai-card", methods=["POST"]) #create card with gemini ai
@jwt_required()
def ai_card():
    """
    This route generates a flashcard for an authenticated user using Google Gemini model gemini-2.5-flash.
    This generation takes the prompt of a question or topic then Gemini will create a front and back json object for flashcard creation
    An optional section field is included to tag the card being created
    Returns: An ai generated flashcard object {id, front, back, section?}
    """
    username = get_jwt_identity()
    data = request.get_json(force=True) or {}
    topic = (data.get("topic") or "").strip() #what the user wants to create a card about
    
    if not topic:
        return jsonify({"error": "topic_required"}), 400 #user must put in a topic for gemini to work

    resp = ai_client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=f'Give one flashcard for the "{topic}" as a single json object with the keys "front" and "back". Return only the json object. Put the question on "front" and the answer on "back".',
    ) #prompt for gemini, basically a user puts in a topic then gemini creates a json flashcard
    
    text = getattr(resp, "text", "") or ""
    text_clean = re.sub(r"^```[a-zA-Z]*\s*|\s*```$","", text.strip()) #removes code fences
    
    try:
        obj = json.loads(text_clean) #puts new text into json object
    except json.JSONDecodeError:
        m = re.search(r"\{\s*\"front\"[\s\S]*\}", text_clean) #tries to clean text with regex if doesn't work
        if not m:
            return jsonify({"error": "bad_json", "preview": text_clean[:200]}), 502 #error handlng if doesn't work
        obj = json.loads(m.group(0))
        
    front = (obj.get("front") or "").strip() #inserts json object into seperate front and back variables
    back = (obj.get("back") or "").strip()
    section = (data.get("section") or "").strip()
    
    if not front or not back:
        return jsonify({"error": "missing_fields", "preview": obj}), 502 #error if either fields unavailable 
    
    card = {"front": front, "back": back, "username": username} #creates flashcard field
    if section:
        card["section"] = section
        
    send_card = db.flashcards.insert_one(card) #adds flashcard to mongo database
    
    flashcard = {
        "id": str(send_card.inserted_id), 
        "front": front, 
        "back": back
    }
    if "section" in card:
        flashcard["section"] = card["section"]
    
    return jsonify(flashcard), 201


@study_bp.route("/ai-card/multi", methods=["POST"])#create multiple ai generated cards at once
@jwt_required()
def ai_card_multi():
    """
    This route generates a flashcards for an authenticated user using Google Gemini model gemini-2.5-flash.
    This generation takes the prompt of a topic inputted by a user, and how many cards of this topic will be created then Gemini will create a front and back json objects based on the amount asked for, for flashcard creation
    An optional section field is included to tag the cards being created
    Returns: Ai generated flashcards {'cards': [{id, front, back, section?}, ...]}
    """
    username = get_jwt_identity()
    data = request.get_json(force=True) or {}
    topic = (data.get("topic") or "").strip()
    raw_count = data.get("count")
    section = (data.get("section") or "").strip()

    if not topic:
        return jsonify({"error": "topic_required"}), 400

    try:
        count = int(raw_count)
    except (TypeError, ValueError):
        return jsonify({"error": "invalid_count"}), 400

    if count <= 0 or count > 30:  #limits users to 30 cards
        return jsonify({"error": "count_out_of_range"}), 400

    # Ask Gemini for multiple flashcards as a JSON array
    prompt = (
        f'Give {count} flashcards for the topic "{topic}" as a JSON array. '
        'Each element must be an object with the keys "front" and "back". '
        'Put the question or prompt on "front" and the answer on "back". '
        'The answer must be brief. '
        'Return only the JSON array.'
    )

    try:
        resp = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
    except Exception as e:
        return jsonify({"error": "ai_error", "detail": str(e)}), 502

    text = getattr(resp, "text", "") or ""

    text_clean = re.sub(r"^```[a-zA-Z]*\s*|\s*```$", "", text.strip())

    try:
        obj = json.loads(text_clean)
    except json.JSONDecodeError:
        m = re.search(r"\[[\s\S]*\]", text_clean)
        if not m:
            return jsonify({"error": "bad_json", "preview": text_clean[:200]}), 502
        obj = json.loads(m.group(0))

    if not isinstance(obj, list) or len(obj) == 0:
        return jsonify({"error": "bad_json_shape", "preview": obj}), 502

    cards_to_insert = []
    for item in obj:
        if not isinstance(item, dict):
            return jsonify({"error": "bad_json_item", "preview": item}), 502

        front = (item.get("front") or "").strip()
        back = (item.get("back") or "").strip()

        if not front or not back:
            return jsonify({"error": "missing_fields", "preview": item}), 502
        
        flashcards = {"front": front, "back": back, "username": username}
        if section:
            flashcards["section"] = section

        cards_to_insert.append(flashcards)

    if not cards_to_insert:
        return jsonify({"error": "no_valid_cards"}), 502

    result = db.flashcards.insert_many(cards_to_insert)

    cards = []
    for inserted_id, fcards in zip(result.inserted_ids, cards_to_insert):
        card = {
            "id": str(inserted_id),
            "front": fcards["front"],
            "back": fcards["back"],
        }
        if "section" in fcards and fcards["section"]:
            card["section"] = fcards["section"]
        cards.append(card)

    return jsonify({"cards": cards}), 201


@study_bp.route("/flashcards", methods=["GET"]) 
@jwt_required()
def get_flashcards():
    """
    This route returns the full list of flashcards of an authenticated user.
    There is a filter where you can return cards that only match the section that you've picked
    Returns: A list of objects(flashcards) {id, front, back, section?}
    """
    username = get_jwt_identity()
    section = request.args.get("section")
    
    query = {"username": username}
    if section and section != "all":
        query["section"] = section
        
    cards = list(db.flashcards.find(query)) #gets list of flashcards from database
    
    
    flashcards = [] 
    for c in cards: #get id, front field and back field of flashcard
        card = { 
            "id": str(c["_id"]), 
            "front": c["front"], 
            "back": c["back"]
            } 
        if "section" in c and c["section"]: #if section exists for the card
            card["section"] = c["section"]
        flashcards.append(card)
    return jsonify(flashcards), 200 #returns json of all flashcards


@study_bp.route("/flashcards", methods=["POST"]) 
@jwt_required()
def create_flashcard():
    """
    This route creates a flashcard for an authenticated user.
    There is an optional 'section' input if a user wants to tag the card they are creating
    Gives an error if required fields (front or back) have no input
    Returns: A new flashcard object {id, front, back, section?}
    """
    username = get_jwt_identity()
    data = request.get_json(force=True) or {} #user input data
    front = (data or {}).get("front", "").strip() #from data get front flashcard field 
    back = (data or {}).get("back", "").strip() #from data get back flashcard field
    section = (data.get("section") or "").strip() #section area to organize flashcards if wanted
    
    if not front or not back:
        return jsonify({"error": "missing_fields"}), 400 #error if either field is not found
    
    card = {"front": front, "back": back, "username": username}
    if section:
        card["section"] = section
    send_card = db.flashcards.insert_one(card) #create a card in database
    flashcard = {
        "id": str(send_card.inserted_id), 
        "front": front, 
        "back": back
    }
    if "section" in card :
        flashcard["section"] = card["section"] #gives card a section if user inputs it
        
    return jsonify(flashcard), 201
        

@study_bp.route("/flashcards/<id>", methods=["DELETE"])
@jwt_required()
def delete_flashcard(id):
    """
    This route takes an authenticated user's flashcard id and erases the flashcard tied to it
    Args:
        id (str): Flashcard id
    Returns: A successful deletion or error if not deleted {deleted, id}
    """
    username = get_jwt_identity()
    try:
        oid = ObjectId(id) #needs id of card to delete it
    except errors.InvalidId:
        return jsonify({"error": "not_found", "id": id}), 404 #if no or incorrect if found then error
    
    delete = db.flashcards.delete_one({"_id": oid, "username": username }) #deletes flashcard
    if delete.deleted_count == 1: #checks if anything got deleted, if not error shows
        return jsonify({"deleted" : True , "id": id}), 200
    else:
        return jsonify({"error": "not_found", "id": id}), 404


@study_bp.route("/flashcards/<id>", methods=["PUT"])
@jwt_required()
def edit_flashcard(id):
    """
    This route edits/updates parts of a flashcard for an authenticated user, this can include the front, back, or section
    Errors show if the card id thats trying to be updated is not found or if no fields are being updated and the user tries to update
    Args:
        id (str): Flashcard id
    Returns: An updated flashcard {id, front, back, section?}
    """
    username = get_jwt_identity()
    try:
        oid = ObjectId(id) #uses flashcard id
    except errors.InvalidId:
        return jsonify({"error": "not_found", "id": id}), 404
    
    #gets flashcard data and puts info into their respective fields
    data = request.get_json(force=True) or {}
    front = data.get("front")
    back = data.get("back")
    section = data.get("section")
    
    if isinstance(front, str): front = front.strip()
    if isinstance(back, str): back = back.strip()
    if isinstance(section, str): section = section.strip()
    update_fields = {} #variable for updating flashcards
    if isinstance(front, str) and front: update_fields["front"] = front
    if isinstance(back, str) and back: update_fields["back"] = back
    if "section" in data:
        if section:
            update_fields["section"] = section
        else:
            update_fields["section"] = None
    
    if not update_fields:
        return jsonify({"error": "invalid_body"}), 400 #if there's no fields being edited then error comes up
    
    query_filter = {"_id": oid, "username": username}
    update_card = {"$set": update_fields}
    card = db.flashcards.find_one_and_update(
        query_filter,
        update_card,
        return_document=ReturnDocument.AFTER,
    ) #finds specific id of card that wants to be updated and then updates it to the user's changes
    
    if card is None: 
        return jsonify({"error": "not_found", "id": id}), 404
    
    flashcards = {
        "id": str(card["_id"]),
        "front": card["front"],
        "back": card["back"]
    }
    
    if "section" in card:
        flashcards["section"] = card["section"]
        
    return jsonify(flashcards), 200


@study_bp.route("/flashcards/<id>", methods=["GET"])
@jwt_required()
def get_flashcard(id):
    """
    This route returns a flashcard of an authenticated user.
    Returns: A flashcard {id, front, back, section?}
    """
    username = get_jwt_identity()
    try:
        oid = ObjectId(id) #uses card id
    except errors.InvalidId:
        return jsonify({"error": "not_found", "id": id}), 404
    
    card = db.flashcards.find_one({"_id": oid, "username":username})
    if card is None: 
        return jsonify({"error": "not_found", "id": id}), 404 
    else: 
        flashcard = {
            "id": str(card["_id"]), 
            "front": card["front"], 
            "back": card["back"]
        }
        if "section" in card and card["section"]:
            flashcard["section"] = card["section"]
        return jsonify(flashcard), 200 #if card is found display its contents


@study_bp.route("/flashcards/multi", methods= ["POST"])
@jwt_required()
def create_multicards():
    """
    This route creates multiple flashcards for an authenticated user.
    There is an optional 'section' input if a user wants to tag the cards they are creating
    Gives an error if required fields (front or back) have no input
    Returns: A list of cards {"cards": [{id, front, back, section?}, ...]}
    """
    username = get_jwt_identity()
    data = request.get_json(force=True) or {} #get json body
    cards = data.get("cards") #takes cards list
    section = (data.get("section") or "").strip()
    
    if not isinstance(cards, list) or len(cards) == 0:
        return jsonify({"error": "invalid_body"}), 400 #error if cards list is empty
    
    cards_to_insert = []
    for raw in cards: #makes sure each card is actually getting made in the proper format
        if not isinstance(raw, dict):
            return jsonify({"error":"invalid_body"}), 400
        
        front = (raw.get("front") or "").strip()
        back = (raw.get("back") or "").strip()
        
        if not front or not back:
            return jsonify({"error": "missing_fields"}), 400
        
        cardsIns = {
            "front": front,
            "back": back,
            "username": username
            }
        if section:
            cardsIns["section"] = section
        
        cards_to_insert.append(cardsIns)
        
    result = db.flashcards.insert_many(cards_to_insert)
    
    created_cards = []
    for inserted_id, fcards in zip(result.inserted_ids, cards_to_insert):
        flashcards = {
            "id" : str(inserted_id),
            "front": fcards["front"],
            "back": fcards["back"],
        }
        if "section" in fcards and fcards["section"]:
            flashcards["section"] = fcards["section"]
        
        created_cards.append(flashcards)
    
    return jsonify({"cards": created_cards}), 201


