from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from routes.users import users_bp   # import the blueprint




app = Flask(__name__)
CORS(app)  # allow frontend to talk to backend

# Load swagger.json from static folder
swagger = Swagger(app, template_file='static/swagger.json')

# Register routes
app.register_blueprint(users_bp)
      
@app.route("/")
def home():
    return "Hello, Flask!"


if __name__ == "__main__":
    app.run(debug=True)
