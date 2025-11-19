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
@jwt_required()
def get_current_user():
    current_username = get_jwt_identity()
    user = get_users_collection().find_one({"username": current_username})

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "data": {
            "username": user["username"],
            "email": user["email"]
        }
    }), 200

 


@users_bp.route("/update", methods=["PUT"])
@jwt_required()
def update_user():
    current_username = get_jwt_identity()
    data = request.get_json()

    new_username = data.get("username")
    new_email = data.get("email")

    users = get_users_collection()

    # Update user info
    users.update_one(
        {"username": current_username},
        {"$set": {"username": new_username, "email": new_email}}
    )

    # Issue new token so frontend stays in sync
    new_token = create_access_token(identity=new_username)

    return jsonify({
        "message": "Profile updated successfully!",
        "token": new_token
    }), 200


# Reset Password
@users_bp.route("/reset_password", methods=["PUT"])
@jwt_required()
def reset_password():
    current_username = get_jwt_identity()
    data = request.get_json()

    password = data.get("password")
    new_password = data.get("new_password")

    if not password or not new_password:
        return jsonify({"error": "Both fields required"}), 400

    users = get_users_collection()
    user = users.find_one({"username": current_username})

    if not user:
        return jsonify({"error": "User not found"}), 404

    # verify old password
    if not check_password_hash(user["password"], password):
        return jsonify({"error": "Incorrect current password"}), 401

    # update new password
    hashed = generate_password_hash(new_password)
    users.update_one(
        {"username": current_username},
        {"$set": {"password": hashed}}
    )

    return jsonify({"message": "Password updated successfully!"}), 200
