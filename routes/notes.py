from threading import Thread
from datetime import datetime, timezone
import hashlib
from bson import ObjectId
from flask_jwt_extended import get_jwt_identity, jwt_required
from database import get_users_collection
from flask import Blueprint, jsonify, request
from services.roadmap_service import generate_roadmap_goals, generate_roadmap_goals_background

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
                "flashcards": "generating",
                "puzzles": "generating",
                "goals": "generating"
            }
    }

    # TODO: Call 3 MVPS here for generation
    Thread(target=generate_roadmap_goals_background, args=(file, str(user["_id"]), str(note["_id"]))).start()
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

    if result.modified_count == 0:
        return jsonify({"error": "Note not found for this user"}), 404

    return jsonify({"message": "Note was deleted"}), 200

