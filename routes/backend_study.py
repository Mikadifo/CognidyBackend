import os, json, re, traceback
from flask import Flask, jsonify, request, Blueprint
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
def ai_card():
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
    if not front or not back:
        return jsonify({"error": "missing_fields", "preview": obj}), 502 #error if either fields unavailable 
    
    doc = {"front": front, "back": back} #creates flashcard field
    ins = db.flashcards.insert_one(doc) #adds flashcard to mongo database
    return jsonify({"id": str(ins.inserted_id), "front": front, "back": back}), 200

@study_bp.route("/ai-card/multi", methods=["POST"])
def ai_card_multi():
    data = request.get_json(force=True) or {}

    topic = (data.get("topic") or "").strip()
    raw_count = data.get("count")

    if not topic:
        return jsonify({"error": "topic_required"}), 400

    try:
        count = int(raw_count)
    except (TypeError, ValueError):
        return jsonify({"error": "invalid_count"}), 400

    if count <= 0 or count > 20:
        return jsonify({"error": "count_out_of_range"}), 400

    # Ask Gemini for multiple flashcards as a JSON array
    prompt = (
        f'Give {count} flashcards for the topic "{topic}" as a JSON array. '
        'Each element must be an object with the keys "front" and "back". '
        'Put the question or prompt on "front" and the answer on "back". The answer should be brief'
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

        cards_to_insert.append({"front": front, "back": back})

    if not cards_to_insert:
        return jsonify({"error": "no_valid_cards"}), 502

    result = db.flashcards.insert_many(cards_to_insert)

    cards = []
    for inserted_id, doc in zip(result.inserted_ids, cards_to_insert):
        cards.append({
            "id": str(inserted_id),
            "front": doc["front"],
            "back": doc["back"],
        })

    return jsonify({"cards": cards}), 200

@study_bp.route("/test-db")
def test_db():
    try:
        client.admin.command('ping')
        return jsonify({"status": "connected"})
    except Exception as e:
        return jsonify({"error": str(e)})
    

@study_bp.route("/flashcards", methods=["GET"]) #route to show all flashcards
def get_flashcards():
    cards = list(db["flashcards"].find()) #gets list of flashcards from database
    flashcards = [{"id": str(c["_id"]), "front": c["front"], "back": c["back"]} for c in cards] #get id, front field and back field of flashcard
    return jsonify(flashcards) #returns json of all flashcards



@study_bp.route("/seed", methods=["POST"])
def seed():
    if db.flashcards.count_documents({}) == 0:
        doc = {"front": "What is Flask?", "back": "A lightweight web framework for Python"}
        inserted = db.flashcards.insert_one(doc)
        return jsonify({"inserted_id": str(inserted.inserted_id), "note": "seeded 1 doc"}), 201
    else:
        return jsonify({"note": "collection not empty — no seed done"}), 200
    
@study_bp.route("/flashcards", methods=["POST"]) #create a flashcard
def create_flashcard():

    data = request.get_json(force=True) #user input data
    front = (data or {}).get("front", "").strip() #from data get front flashcard field 
    back = (data or {}).get("back", "").strip() #from data get back flashcard field
    
    if not front or not back:
        return jsonify({"error": "Please write for both the front and the back."}) #error if either field is not found
    
    card = {"front": front, "back": back}
    send_card = db.flashcards.insert_one(card) #create a card in database
    return jsonify({"id": str(send_card.inserted_id), "front": front, "back": back}), 201
        

@study_bp.route("/flashcards/<id>", methods=["DELETE"])
def delete_flashcard(id):
    try:
        oid = ObjectId(id) #needs id of card to delete it
    except errors.InvalidId:
        return jsonify({"error": "not_found", "id": id}), 404 #if no or incorrect if found then error
    
    delete = db.flashcards.delete_one({"_id": oid}) #deletes flashcard
    if delete.deleted_count == 1: #checks if anything got deleted, if not error shows
        return jsonify({"status": "deleted", "id": id}), 200
    else:
        return jsonify({"error": "not_found", "id": id}), 404


@study_bp.route("/flashcards/<id>", methods=["PUT"]) #route to edit a flashcard
def edit_flashcard(id):
    try:
        oid = ObjectId(id) #uses flashcard id
    except errors.InvalidId:
        return jsonify({"error": "not_found", "id": id}), 404
    
    #gets flashcard data and puts info into their respective fields
    data = request.get_json(force=True) or {}
    front = data.get("front")
    back = data.get("back")
    
    if isinstance(front, str): front = front.strip()
    if isinstance(back, str): back = back.strip()
    update_fields = {} #variable for updating flashcards
    if isinstance(front, str) and front: update_fields["front"] = front
    if isinstance(back, str) and back: update_fields["back"] = back
    if not update_fields:
        return jsonify({"error": "invalid_body"}), 400 #if there's no fields being edited then error comes up
    
    filter = {"_id": oid}
    update_card = {"$set": update_fields}
    card = db.flashcards.find_one_and_update(
        filter,
        update_card,
        return_document=ReturnDocument.AFTER,
    ) #finds specific id of card that wants to be updated and then updates it to the user's changes
    
    if card is None: 
        return jsonify({"error": "not_found", "id": id}), 404 
    else: 
        return jsonify({ "id": str(card["_id"]), "front": card["front"], "back": card["back"] }), 200

@study_bp.route("/flashcards/<id>", methods=["GET"]) #get and show specific card
def get_flashcard(id):
    try:
        oid = ObjectId(id) #uses card id
    except errors.InvalidId:
        return jsonify({"error": "not_found", "id": id}), 404
    
    card = db.flashcards.find_one({"_id": oid})
    if card is None: 
        return jsonify({"error": "not_found", "id": id}), 404 
    else: 
        return jsonify({ "id": str(card["_id"]), "front": card["front"], "back": card["back"] }), 200 #if card is found display its contents


@study_bp.route("/flashcards/multi", methods= ["POST"])
def create_multicards():
    data = request.get_json() or {} #get json body
    
    cards = data.get("cards") #takes cards list
    if not isinstance(cards, list) or len(cards) == 0:
        return jsonify({"error": "invalid_body"}), 400 #error if cards list is empty
    
    cards_to_insert = []
    for raw in cards: #makes sure each card is actually getting made in the proper format
        if not isinstance(raw, dict):
            return jsonify({"error":"invalid_body"}), 400
        
        front = (raw.get("front") or "").strip()
        back = (raw.get("back") or "").strip()
        
        if not front or not back:
            return jsonify({"error": "Please write for both the front and the back."}), 400
        
        cards_to_insert.append({"front": front, "back": back})
        
    result = db.flashcards.insert_many(cards_to_insert)
    
    created_cards = []
    for inserted_id, cards in zip(result.inserted_ids, cards_to_insert):
        created_cards.append({
            "id" : str(inserted_id),
            "front": cards["front"],
            "back": cards["back"],
        })
    
    return jsonify({"cards": created_cards}), 201