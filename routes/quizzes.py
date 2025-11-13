from flask_jwt_extended import get_jwt_identity, jwt_required
from database import get_quizzes_collection, get_users_collection
from flask import Blueprint, jsonify

quizzes_bp = Blueprint("quizzes", __name__)

@quizzes_bp.route("/", methods=["GET"])
@jwt_required()
def get_goals():
    username = get_jwt_identity()

    user = get_users_collection().find_one({"username": username})
    if not user:
        return jsonify({"error": "User not found"}), 404

    quizzes = get_quizzes_collection().find({"user_id": str(user["_id"])}, {"user_id": 0})
    quizzes.sort("order")
    quizzes = quizzes.to_list()

    return jsonify({"message": "Quizzes retrieved successfully", "data": quizzes}), 200
