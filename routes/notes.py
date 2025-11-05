import os
from threading import Thread
from datetime import datetime, timezone
import hashlib
from bson import ObjectId
from flask_jwt_extended import get_jwt_identity, jwt_required
from controllers.goals_controller import delete_user_goal
from database import get_roadmap_goals_collection, get_users_collection
from flask import Blueprint, jsonify, request
from services.roadmap_service import generate_roadmap_goals_background

MAX_UPLOADS = 5
notes_bp = Blueprint("notes", __name__)

@notes_bp.route("/", methods=["GET"])
@jwt_required()
def get_notes():
    username = get_jwt_identity()

    user = get_users_collection().find_one({"username": username})
    if not user:
        return jsonify({"error": "User not found"}), 404

    user_notes = user.get("notes", [])

    for note in user_notes:
        if "_id" in note:
            note["_id"] = str(note["_id"])

    return jsonify({"message": "Notes retrieved successfully", "data": user_notes}), 200

@notes_bp.route("/upload/guest", methods=["POST"])
def upload_guest():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # data = TODO: call each MVP generate service, but roadmap_service
    data = {} # of type {flashcards: [], puzzles: []}

    return jsonify({"message": "Content generated for guest user", "data": data}), 200

@notes_bp.route("/upload/auth", methods=["POST"])
@jwt_required()
def upload_auth():
    username = get_jwt_identity()

    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    user = get_users_collection().find_one({"username": username})
    if not user:
        return jsonify({"error": "User not found"}), 404

    user_notes = user.get("notes", [])
    if len(user_notes) >= MAX_UPLOADS:
        return jsonify({"error": f"Upload limit reached ({MAX_UPLOADS})"}), 403

    file_bytes = file.read()
    file_hash = hashlib.sha256(file_bytes).hexdigest()
    file.seek(0)

    note_hashes = [n.get("hash") for n in user_notes]
    if file_hash in note_hashes:
        return jsonify({"error": "This file has already been uploaded"}), 400

    note = {
            "_id": ObjectId(),
            "filename": file.filename,
            "hash": file_hash,
            "created_at": datetime.now(timezone.utc),
            "status": {
                "flashcards": "done", # TODO: set to generating once service is implemented
                "puzzles": "done", # TODO: set to generating once service is implemented
                "goals": "generating"
            }
    }

    # TODO: Call 3 MVPS Threads here for generation
    file_bytes = file.read()
    file_ext = os.path.splitext(str(file.filename))[1]
    goals_thread = Thread(target=generate_roadmap_goals_background, args=(file_bytes, file_ext, str(user["_id"]), str(note["_id"])))
    goals_thread.start()
    # TODO: call generate flashcards
    # TODO: call generate puzzles

    get_users_collection().find_one_and_update({"username": username}, {"$push": {"notes": note}})

    note["_id"] = str(note["_id"])

    return jsonify({"message": "File uploaded successfully", "data": note }), 202

@notes_bp.route("/delete/<note_id>", methods=["DELETE"])
@jwt_required()
def delete_note(note_id):
    username = get_jwt_identity()

    user = get_users_collection().find_one({"username": username})
    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        note_oid = ObjectId(note_id)
    except Exception:
        return jsonify({"error": "Invalid note ID"}), 400

    result = get_users_collection().update_one({"username": username}, {"$pull": {"notes": {"_id": note_oid}}})

    goals = get_roadmap_goals_collection().find({"note_id": note_id})
    goals.sort("order", -1)
    goals = goals.to_list()

    for goal in goals:
        if goal["note_id"] == note_id:
            delete_user_goal(goal, str(user["_id"]))

    if result.modified_count == 0:
        return jsonify({"error": "Note not found for this user"}), 404

    return jsonify({"message": "Note was deleted"}), 200


@notes_bp.route("/status/<note_id>", methods=["GET"])
@jwt_required()
def get_note_status(note_id):
    username = get_jwt_identity()

    user = get_users_collection().find_one({"username": username})
    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        note_oid = ObjectId(note_id)
    except Exception:
        return jsonify({"error": "Invalid note ID"}), 400

    if "notes" not in user or len(user["notes"]) <= 0:
        return jsonify({"message": "User does not have uploaded notes"}), 404
    
    notes = user["notes"]
    user_note = {}

    for note in notes:
        if note["_id"] == note_oid:
            user_note = note

    if not user_note:
        return jsonify({"message": "User note not found"}), 404

    return jsonify({"message": "Fetched status successfully", "data": user_note["status"]}), 200

