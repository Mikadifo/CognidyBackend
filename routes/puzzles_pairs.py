from flask_jwt_extended import get_jwt_identity, jwt_required
from database import get_puzzles_collection, get_users_collection
from flask import Blueprint, jsonify
import random

puzzles_pair_bp = Blueprint("puzzles-pairs", __name__)


@puzzles_pair_bp.route("/", methods=["GET"])
@jwt_required()
def get_puzzles():
    username = get_jwt_identity()

    user = get_users_collection().find_one({"username": username})
    if not user:
        return jsonify({"error": "User not found"}), 404

    puzzles = get_puzzles_collection().find({"user_id": str(user["_id"])}, {"user_id": 0})
    puzzles = puzzles.to_list()
    random.shuffle(puzzles)

    user_notes = {str(note["_id"]): note["filename"] for note in user.get("notes", [])}

    for puzzle in puzzles:
        puzzle["_id"] = str(puzzle["_id"])

        if "note_id" in puzzle:
            puzzle["sourceFileName"] = user_notes.get(puzzle["note_id"], None)
            del puzzle["note_id"]

    return jsonify({"message": "Puzzles retrieved successfully", "data": puzzles}), 200
