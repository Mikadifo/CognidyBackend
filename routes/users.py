import bcrypt
from database import get_db, get_users_collection
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    # Insert user
    get_users_collection().insert_one(
        {"username": username, "email": email, "password": hashed_pw}
    )

    return jsonify({"message": "Signup successful!"}), 201


# Login route
@users_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Username and password required"}), 400

    user = get_users_collection().find_one({"username": username})

    if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401
