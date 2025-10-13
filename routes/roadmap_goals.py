from bson import ObjectId
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError
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
        user = get_users_collection().find_one({"username": username}, {"user_id": 1})

        if not user:
            return jsonify({"error": "User not found"}), 404

        goals = get_roadmap_goals_collection().find({"user_id": str(user["_id"])}, {"order": 1})
        goals.sort("order")
        goals = goals.to_list()
        goals_size = len(goals)

        if goals_size >= MAX_GOALS:
            return jsonify({"error": f"You can only have up to {MAX_GOALS} goals"}), 409

        new_goal = goal.model_dump()
        new_goal["_id"] = ObjectId()
        new_goal["user_id"] = str(user["_id"])

        if new_goal["order"] > goals[goals_size - 1]["order"] + 1:
            new_goal["order"] = goals[goals_size - 1]["order"] + 1
            get_roadmap_goals_collection().insert_one(new_goal)

            return jsonify({"message": "Roadmap Goal created successfully"}), 201

        get_roadmap_goals_collection().update_many(
                {"user_id": str(user["_id"]), "order": {"$gte": new_goal["order"]}},
                {"$inc": {"order": 1}}
        )
        get_roadmap_goals_collection().insert_one(new_goal)

        return jsonify({"message": "Roadmap Goal created successfully"}), 201
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

    get_roadmap_goals_collection().update_many(
            {"user_id": str(user["_id"]), "order": {"$gt": goal_to_delete["order"]}},
            {"$inc": {"order": -1}}
    )

    get_roadmap_goals_collection().delete_one({"_id": goal_to_delete["_id"], "user_id": str(user["_id"])})

    return jsonify({"message": "Goal was deleted"}), 200

