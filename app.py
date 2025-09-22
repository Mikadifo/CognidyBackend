from flask import Flask, request, jsonify
from flask_cors import CORS
from flasgger import Swagger
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


app = Flask(__name__)
CORS(app)  # allow frontend to talk to backend
Swagger(app)

# Connect to MongoDB
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["cognidy_db"]  # database name
users = db["users"]        # collection name

@app.route("/")
def home():
    return "Hello, Flask!"

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if users.find_one({"username": username}):
        return jsonify({"message": "Username already exists"}), 400

    users.insert_one({
        "username": username,
        "email": email,
        "password": password  # later hash this!
    })

    return jsonify({"message": "Signup successful!"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = users.find_one({"username": username, "password": password})
    if user:
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

if __name__ == "__main__":
    app.run(debug=True)
