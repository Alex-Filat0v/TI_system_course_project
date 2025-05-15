from flask import Flask
from flask_cors import CORS
from flask_session import Session
from flask_jwt_extended import JWTManager

from routes.user_routes import user_blueprint
from routes.api_routes import api_blueprint

app = Flask(__name__)
app.secret_key = "11"
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

app.config["JWT_SECRET_KEY"] = "111"
jwt = JWTManager(app)

CORS(app)

app.register_blueprint(user_blueprint, url_prefix="/")
app.register_blueprint(api_blueprint, url_prefix="/api")

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
