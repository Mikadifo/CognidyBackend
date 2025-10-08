# Create Blueprint
from datetime import datetime, timezone
import hashlib
from bson import ObjectId
from flask_jwt_extended import get_jwt_identity, jwt_required
from database import get_db, get_users_collection
from flask import Blueprint, jsonify, request

from services.notes_service import generate_content

MAX_UPLOADS = 5

notes_bp = Blueprint("notes", __name__)

# MongoDB setup
db = get_db()

@notes_bp.route("/upload/guest", methods=["POST"])
def upload_guest():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    data = generate_content(file, True)

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

    data = generate_content(file, False)
    # TODO: store data in DB

    note = {
            "_id": ObjectId(),
            "filename": file.filename,
            "hash": file_hash,
            "created_at": datetime.now(timezone.utc)
    }
    get_users_collection().find_one_and_update({"username": username}, {"$push": {"notes": note}})

    return jsonify({"message": "File uploaded successfully"}), 200
