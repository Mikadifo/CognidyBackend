from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended.utils import create_access_token
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import get_users_collection
from flask import Blueprint, request, jsonify

# Create Blueprint
users_bp = Blueprint("users", __name__)

# Signup route
@users_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"message": "All fields are required"}), 400

    # Check if user already exists
    if get_users_collection().find_one({"username": username}):
        return jsonify({"message": "Username already exists"}), 400

    # Hash the password
    hashed_pw = generate_password_hash(password)

    # Insert user
    get_users_collection().insert_one(
        {"username": username, "email": email, "password": hashed_pw}
    )

    access_token = create_access_token(identity=username)

    return jsonify({"message": "Signup successful!", "data": access_token}), 201


# Login route
@users_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Username and password required"}), 400

    user = get_users_collection().find_one({"username": username})

    if user and check_password_hash(user["password"], password):
        access_token = create_access_token(identity=user["username"])
        return jsonify({"message": "Login successful", "data": access_token}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401
    
    
    # Get current user info
@users_bp.route("/me", methods=["GET"])
@jwt_required()  # ensures user must send valid token
def get_current_user():
    current_user = get_jwt_identity()
    user = get_users_collection().find_one({"username": current_user})

    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "username": user["username"],
        "email": user["email"]
    }), 200

@users_bp.route("/update", methods=["PUT"])
@jwt_required()
def update_user():
    current_user = get_jwt_identity()
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")

    users = get_users_collection()
    users.update_one({"username": current_user}, {"$set": {"username": username, "email": email}})

    return jsonify({"message": "Profile updated successfully!"}), 200
