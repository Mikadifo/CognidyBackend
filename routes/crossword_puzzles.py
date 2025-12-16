# routes/crossword_puzzles.py
from flask import Blueprint, request, jsonify
from services.puzzles_service import generate_crossword_puzzle

crossword_bp = Blueprint('crosswords', __name__)

@crossword_bp.route('/generate', methods=['POST'])
def generate_crossword():
    """Generate crossword puzzle from uploaded file (guest-only)"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file uploaded"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "error": "No file selected"}), 400
        
        # Generate crossword puzzle
        result = generate_crossword_puzzle(file)
        
        if result["success"]:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500

@crossword_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200