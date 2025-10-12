from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended.utils import create_access_token
from database import get_db, get_users_collection
from flask import Blueprint, request, jsonify

# Create Blueprint
users_bp = Blueprint("users", __name__)

# MongoDB setup
db = get_db()

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

    return jsonify({"message": "Signup successful!", "access_token": access_token}), 201


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
        return jsonify({"message": "Login successful", "access_token": access_token}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401
