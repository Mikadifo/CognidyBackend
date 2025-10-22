from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError
from controllers.goals_controller import create_user_goal, delete_user_goal, get_user_goals_count
from database import get_roadmap_goals_collection, get_users_collection
from flask import Blueprint, jsonify, request

from models.roadmap_goal import MAX_GOALS, RoadmapGoal

roadmap_bp = Blueprint("roadmap_goals", __name__)

@roadmap_bp.route("/", methods=["GET"])
@jwt_required()
def get_goals():
    username = get_jwt_identity()

    user = get_users_collection().find_one({"username": username})
    if not user:
        return jsonify({"error": "User not found"}), 404

    goals = get_roadmap_goals_collection().find({"user_id": str(user["_id"])}, {"_id": 0, "user_id": 0})
    goals.sort("order")
    goals = goals.to_list()

    return jsonify({"message": "Notes retrieved successfully", "data": goals}), 200

@roadmap_bp.route("/new", methods=["POST"])
@jwt_required()
def create_goal():
    try:
        username = get_jwt_identity()
        data = request.get_json()
        goal = RoadmapGoal(**data)
        new_goal = goal.model_dump()
        user = get_users_collection().find_one({"username": username}, {"user_id": 1})

        if not user:
            return jsonify({"error": "User not found"}), 404


        goals_size = get_user_goals_count(str(user["_id"]))

        if goals_size >= MAX_GOALS:
            return jsonify({"error": f"You can only have up to {MAX_GOALS} goals"}), 409

        return create_user_goal(str(user["_id"]), new_goal, None)
    except ValidationError as error:
        first_error = error.errors()[0]
        return jsonify({"error": first_error.get("msg")}), 400

@roadmap_bp.route("/delete/<int:goal_order>", methods=["DELETE"])
@jwt_required()
def delete_goal(goal_order):
    username = get_jwt_identity()

    user = get_users_collection().find_one({"username": username})
    if not user:
        return jsonify({"error": "User not found"}), 404

    goal_to_delete = get_roadmap_goals_collection().find_one({"user_id": str(user["_id"]), "order": goal_order}, {"order": 1, "_id": 1})

    if not goal_to_delete:
        return jsonify({"error": "Goal does not exists for this user"}), 404

    return delete_user_goal(goal_to_delete, str(user["_id"]))

@roadmap_bp.route("/complete/<int:goal_order>", methods=["PUT"])
@jwt_required()
def set_goal_completion(goal_order):
    username = get_jwt_identity()
    data = request.get_json()
    completed = data.get("completed")

    if completed is None:
        return jsonify({"error": "Missing 'completed' field"}), 400

    user = get_users_collection().find_one({"username": username})
    if not user:
        return jsonify({"error": "User not found"}), 404

    order_filter = {"$gte": goal_order}

    if completed:
        order_filter = goal_order

    result = get_roadmap_goals_collection().update_many(
            {"user_id": str(user["_id"]), "order": order_filter},
            {"$set": {"completed": completed}}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Goal not found"}), 404

    return jsonify({"message": "Goal completion updated"}), 200
