from flask import Flask
from google.cloud import firestore
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    CORS(app)
    
    # Initialise Firestore
    db = firestore.Client()
    app.db = db
    
    # Register blueprints
    from app.routes import main as main_blueprint
    from app.auth import auth as auth_blueprint
    
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)
    
    return app