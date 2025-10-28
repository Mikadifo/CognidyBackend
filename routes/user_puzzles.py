from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.puzzles_service import generate_user_puzzles

puzzles_bp = Blueprint('puzzles', __name__)

@puzzles_bp.route('/generate', methods=['POST'])
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

@puzzles_bp.route('/my-puzzles', methods=['GET'])
@jwt_required()
def get_user_puzzles():
    try:
        user_id = get_jwt_identity()
        from database import get_collection
        from constants.collections import Collection
        
        puzzles_collection = get_collection(Collection.THE_PUZZLES)
        user_puzzles = list(puzzles_collection.find({"user_id": user_id}))
        
        # Convert ObjectId to string
        for puzzle in user_puzzles:
            puzzle["_id"] = str(puzzle["_id"])
        
        return jsonify({
            "success": True,
            "puzzles": user_puzzles
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500