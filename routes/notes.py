# Create Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required
from database import get_db
from flask import Blueprint, jsonify, request

from services.notes_service import generate_content

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
    print(username)

    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    data = generate_content(file, False)
    # TODO: store data in DB

    return jsonify({"message": "Works"}), 200
