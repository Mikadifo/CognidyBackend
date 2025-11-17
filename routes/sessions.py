from flask_jwt_extended import get_jwt_identity, jwt_required
from database import get_sessions_collection, get_users_collection
from flask import Blueprint, jsonify, request

sessions_bp = Blueprint("sessions", __name__)

@sessions_bp.route("/", methods=["GET"])
@jwt_required()
def get_notes():
    username = get_jwt_identity()

    user = get_users_collection().find_one({"username": username})
    if not user:
        return jsonify({"error": "User not found"}), 404

    sessions = get_sessions_collection().find({"user_id": str(user["_id"])}, {"_id": 0})
    sessions.sort({"name": 1})
    sessions = sessions.to_list()

    return jsonify({"message": "Sessions retrieved successfully", "data": sessions}), 200

# @notes_bp.route("/upload/guest", methods=["POST"])
# def upload_guest():
