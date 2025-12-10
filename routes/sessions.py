from datetime import datetime, timezone
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError
from controllers.session_controller import get_next_session_number
from database import get_sessions_collection, get_users_collection
from flask import Blueprint, jsonify, request

from models.session import Session

sessions_bp = Blueprint("sessions", __name__)

@sessions_bp.route("/", methods=["GET"])
@jwt_required()
def get_sessions():
    username = get_jwt_identity()

    user = get_users_collection().find_one({"username": username})
    if not user:
        return jsonify({"error": "User not found"}), 404

    sessions = get_sessions_collection().find({"user_id": str(user["_id"])}, {"_id": 0})
    sessions.sort({"name": 1})
    sessions = sessions.to_list()

    return jsonify({"message": "Sessions retrieved successfully", "data": sessions}), 200

@sessions_bp.route("/add", methods=["POST"])
@jwt_required()
def add_session():
    try:
        username = get_jwt_identity()
        data = request.get_json()
        session = Session(**data)
        new_session = session.model_dump()
        user = get_users_collection().find_one({"username": username}, {"_id": 1})

        if not user:
            return jsonify({"error": "User not found"}), 404

        new_session["number"] = get_next_session_number(user["_id"], new_session["section"])
        new_session["completed_at"] = datetime.combine(new_session["completed_at"], datetime.min.time(), tzinfo=timezone.utc)
        new_session["user_id"] = str(user["_id"])
        created = get_sessions_collection().insert_one(new_session)

        if created:
            return jsonify({"message": "Session created successfully"}), 201
        else:
            return jsonify({"error": "Error while saving session"}), 500
    except ValidationError as error:
        errors = {error["loc"][0]: error["msg"] for error in error.errors()}
        return jsonify({"error": errors}), 400
