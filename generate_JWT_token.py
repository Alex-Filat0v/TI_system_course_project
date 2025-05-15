from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token
from datetime import timedelta

app = Flask(__name__)

secret = str(input("Введите JWT SECRET KEY для генерации токена доступа: "))

app.config['JWT_SECRET_KEY'] = f'{secret}'

jwt = JWTManager(app)

with app.app_context():
    token = create_access_token(identity="admin", expires_delta=timedelta(days=1))
    print(token)
