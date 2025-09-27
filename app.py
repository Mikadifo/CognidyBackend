from flask import Flask
from database import get_db, get_thesaurus_collection, get_users_collection
from flask import jsonify
from flask import Blueprint, Flask
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

# Get database instance (connection handled in database.py)
db = get_db()
api_bp = Blueprint("api", __name__)

@api_bp.route("/", methods=['GET'])
def home():
    return "Hello!"

SWAGGER_URL = '/docs'
API_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config = { 'app_name': "Cognidy API" }
        )

app.register_blueprint(swaggerui_blueprint, url_prefix = SWAGGER_URL)
app.register_blueprint(api_bp, url_prefix="/api")

# TODO: remove this, just testing
@app.route("/users", methods = ["GET"])
def get_test_user():
    user = get_users_collection().find_one()
    if not user:
        return jsonify({"error": "No user found"}), 404
    user["_id"] = str(user["_id"])
    return jsonify(user), 200

if __name__ == "__main__":
    app.run(debug=True)
