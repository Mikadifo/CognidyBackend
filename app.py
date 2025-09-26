from flask import Flask
from database import get_db, get_thesaurus_collection, get_users_collection
from flask import jsonify

app = Flask(__name__)

# Get database instance (connection handled in database.py)
db = get_db()

@app.route("/")
def home():
    return "Hello, Flask!"

@app.route("/users", methods = ["GET"])
def get_test_user():
    user = get_users_collection().find_one()
    if not user:
        return jsonify({"error": "No user found"}), 404
    user["_id"] = str(user["_id"])
    return jsonify(user), 200

if __name__ == "__main__":
    app.run(debug=True)
