from flask import Flask
from app.db import init_db

def create_app():
    app = Flask(__name__)
    app.secret_key = "9f2e4a729dbb8a98424df3d917e8b8a89af38b1234567890aabbccddeeff0011"

    init_db()

    from app.routes import main
    from app.auth import auth

    app.register_blueprint(main)
    app.register_blueprint(auth)

    return app
