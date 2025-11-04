import os, json, re, traceback
from flask import Flask, jsonify, request, Blueprint
from flask_cors import CORS
from pymongo import MongoClient
from pymongo import ReturnDocument
from dotenv import load_dotenv
from bson import ObjectId, errors
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


# @study_bp.route("/ai-test", methods=["GET"])
# def ai_test():
#     try:
#         resp = ai_client.models.generate_content(
#             model="gemini-2.5-flash", 
#             contents="Why is the sky blue? One short sentence.",
#         )
#         text = getattr(resp, "text", "") or ""
#         if not text: 
#             text = "\n".join(
#                 (getattr(x, "text", "") or "")
#                 for c in (getattr(resp, "candidates", []) or [])
#                 for x in (getattr(getattr(c, "content", {}), "parts", []) or [])
#                 if getattr(x, "text", "") 
#             )
#         return jsonify({"text": text}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
    


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
