# app/auth.py
from functools import wraps
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
import jwt
import datetime
import os

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            token = token.split(' ')[1]
            data = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=['HS256'])
            current_user = get_user_by_id(data['user_id'])
            if not current_user:
                return jsonify({'error': 'Invalid token'}), 401
        except:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

def get_user_by_id(user_id):
    user_doc = db.collection('users').document(user_id).get()
    if user_doc.exists:
        return {'id': user_id, **user_doc.to_dict()}
    return None

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    user_ref = db.collection('users').where('email', '==', data['email']).limit(1).get()
    if len(list(user_ref)) > 0:
        return jsonify({'error': 'User already exists'}), 400
    
    new_user = {
        'email': data['email'],
        'password': generate_password_hash(data['password']),
        'created_at': datetime.datetime.now()
    }
    
    user_ref = db.collection('users').add(new_user)
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    user_ref = db.collection('users').where('email', '==', data['email']).limit(1).get()
    
    for user in user_ref:
        if check_password_hash(user.to_dict()['password'], data['password']):
            token = jwt.encode({
                'user_id': user.id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
            }, os.getenv('SECRET_KEY'), algorithm='HS256')
            return jsonify({'token': token}), 200
            
    return jsonify({'error': 'Invalid credentials'}), 401
