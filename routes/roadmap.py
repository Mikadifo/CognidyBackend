from flask_jwt_extended import get_jwt_identity, jwt_required
from database import get_db, get_roadmap_goals_collection, get_users_collection
from flask import Blueprint, jsonify

roadmap_bp = Blueprint("roadmap", __name__)

# MongoDB setup
db = get_db()

@roadmap_bp.route("/goals", methods=["GET"])
@jwt_required()
def get_goals():
    username = get_jwt_identity()

    user = get_users_collection().find_one({"username": username})
    if not user:
        return jsonify({"error": "User not found"}), 404

    roadmap_goals = get_roadmap_goals_collection().find({"user_id": str(user["_id"])}, {"_id": 0, "user_id": 0})
    roadmap_goals.sort("order")
    roadmap_goals = roadmap_goals.to_list()

    return jsonify({"message": "Notes retrieved successfully", "data": roadmap_goals})
