from datetime import timedelta
from flask import Flask, Response, request
from flask import Blueprint, Flask
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from config.env_config import get_env_config
from routes.users import users_bp
from routes.notes import notes_bp
from routes.roadmap_goals import roadmap_bp
from flask_jwt_extended import JWTManager
from routes.puzzles import puzzles_bp

env = get_env_config()

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = env.JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=15)

jwt = JWTManager(app)
CORS(
    app,
    origins=["http://localhost:3000", "https://cognidy-frontend.vercel.app"],
    supports_credentials=True,
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

@app.before_request
def handle_options():
    if request.method == 'OPTIONS':
        return Response(status=200)

# Get database instance (connection handled in database.py)
api_bp = Blueprint("api", __name__)


SWAGGER_URL = "/api/v1/docs"
API_URL = "/static/swagger.json"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "Cognidy API"}
)


@api_bp.route("/", methods=["GET"])
def home():
    return "Hello!"

@app.route('/')
def home_default():
    return "Hello, World!"


# Register blueprints
app.register_blueprint(api_bp, url_prefix="/api")
app.register_blueprint(users_bp, url_prefix="/api/users")
app.register_blueprint(notes_bp, url_prefix="/api/notes")
app.register_blueprint(roadmap_bp, url_prefix="/api/roadmap_goals")
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
app.register_blueprint(puzzles_bp, url_prefix="/api/puzzles")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)

# Note: need to implement t
