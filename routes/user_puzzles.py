from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import get_puzzles_collection  # Fixed import
from services.puzzles_service import generate_user_puzzles
from config.env_config import get_env_config
from bson import ObjectId

env = get_env_config()
puzzles_bp = Blueprint('puzzles', __name__)

@puzzles_bp.route('/generate', methods=['POST'])  # Added generate route
@jwt_required()
def generate_puzzle():
    try:
        user_id = get_jwt_identity()
        
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Generate puzzle
        result = generate_user_puzzles(file, user_id)
        
        if result is None:
            return jsonify({"error": "Failed to generate puzzle"}), 500
        
        return jsonify({
            "success": True,
            "puzzle": result
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@puzzles_bp.route('/', methods=['GET'])
@jwt_required()
def get_user_puzzles():
    try:
        user_id = get_jwt_identity()
        puzzles_collection = get_puzzles_collection()
        user_puzzles = list(puzzles_collection.find({"user_id": user_id}))
        
        # Convert ObjectId to string
        for puzzle in user_puzzles:
            puzzle["_id"] = str(puzzle["_id"])
            # Ensure created_at is serializable
            if 'created_at' in puzzle:
                puzzle["created_at"] = puzzle["created_at"].isoformat()
            if 'completion_time' in puzzle and puzzle["completion_time"]:
                puzzle["completion_time"] = puzzle["completion_time"].isoformat()
        
        return jsonify({
            "success": True,
            "puzzles": user_puzzles
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@puzzles_bp.route('/<puzzle_id>', methods=['DELETE'])  # Fixed route - use URL parameter
@jwt_required()
def delete_user_puzzle(puzzle_id):
    try:
        user_id = get_jwt_identity()
        puzzles_collection = get_puzzles_collection()
        
        # Convert string ID to ObjectId for MongoDB
        try:
            object_id = ObjectId(puzzle_id)
        except:
            return jsonify({"error": "Invalid puzzle ID format"}), 400
            
        result = puzzles_collection.delete_one({"_id": object_id, "user_id": user_id})

        if result.deleted_count == 0:
            return jsonify({"error": "Puzzle not found or not owned by user"}), 404

        return jsonify({"message": "Puzzle deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@puzzles_bp.route('/<puzzle_id>/complete', methods=['PUT'])  # Added completion route
@jwt_required()
def complete_puzzle(puzzle_id):
    try:
        user_id = get_jwt_identity()
        puzzles_collection = get_puzzles_collection()
        
        try:
            object_id = ObjectId(puzzle_id)
        except:
            return jsonify({"error": "Invalid puzzle ID format"}), 400
        
        # Get completion time from request (optional)
        completion_time = request.json.get('completion_time') if request.json else None
        
        update_data = {
            "completed": True,
            "completion_time": datetime.utcnow() if not completion_time else datetime.fromisoformat(completion_time)
        }
        
        result = puzzles_collection.update_one(
            {"_id": object_id, "user_id": user_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({"error": "Puzzle not found or not owned by user"}), 404
            
        return jsonify({"message": "Puzzle marked as completed"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500