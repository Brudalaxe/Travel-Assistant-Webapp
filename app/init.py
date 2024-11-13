# app/__init__.py
from flask import Flask
from google.cloud import firestore
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
CORS(app)

# Initialize Firestore
db = firestore.Client()

from app import routes
