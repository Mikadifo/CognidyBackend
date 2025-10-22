from flask import jsonify
from bson import ObjectId
from database import get_roadmap_goals_collection


def get_user_goals_count(user_id):
    return get_roadmap_goals_collection().count_documents({"user_id": user_id})

def delete_user_goal_by_id(goal_id, user_id):
    goal_to_delete = get_roadmap_goals_collection().find_one({"_id": goal_id}, {"order": 1, "_id": 1})

    if not goal_to_delete:
        return jsonify({"error": "Goal does not exists for this user"}), 404

    delete_user_goal(goal_to_delete, user_id)

def delete_user_goal(goal, user_id):
    get_roadmap_goals_collection().update_many(
            {"user_id": user_id, "order": {"$gt": goal["order"]}},
            {"$inc": {"order": -1}}
    )

    get_roadmap_goals_collection().delete_one({"_id": ObjectId(goal["_id"]), "user_id": user_id})

    return jsonify({"message": "Goal was deleted"}), 200

def create_user_goal(user_id, new_goal, file_id):
    goals = get_roadmap_goals_collection().find({"user_id": user_id}, {"order": 1, "completed": 1})
    goals.sort("order")
    goals = goals.to_list()
    goals_size = len(goals)

    new_goal["_id"] = ObjectId()
    new_goal["user_id"] = user_id
    if file_id is not None:
        new_goal["note_id"] = file_id

    if len(goals) == 0:
        get_roadmap_goals_collection().insert_one(new_goal)
        return jsonify({"message": "Roadmap Goal created successfully"}), 201

    new_order = new_goal["order"]

    if new_order > goals[goals_size - 1]["order"] + 1:
        new_goal["order"] = goals[goals_size - 1]["order"] + 1
        get_roadmap_goals_collection().insert_one(new_goal)

        return jsonify({"message": "Roadmap Goal created successfully"}), 201

    new_goal["completed"] = goals[new_order - 1]["completed"]

    get_roadmap_goals_collection().update_many(
            {"user_id": user_id, "order": {"$gte": new_goal["order"]}},
            {"$inc": {"order": 1}}
    )
    get_roadmap_goals_collection().insert_one(new_goal)

    return jsonify({"message": "Roadmap Goal created successfully"}), 201
