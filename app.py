from flask import Blueprint, Flask
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from routes.users import users_bp   # import the blueprint

app = Flask(__name__)
CORS(app)  # allow frontend to talk to backend

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

# Register blueprints
app.register_blueprint(users_bp, url_prefix="/users)
app.register_blueprint(swaggerui_blueprint, url_prefix = SWAGGER_URL)
app.register_blueprint(api_bp, url_prefix="/api")

if __name__ == "__main__":
    app.run(debug=True)
