from flask import Flask
from app.db import init_db
from dotenv import load_dotenv

def create_app():
    load_dotenv()
    init_db()
    app = Flask(__name__)
    return app
