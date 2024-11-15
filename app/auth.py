from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jwt
import datetime
import os

auth = Blueprint('auth', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token.split(' ')[1]
                
            data = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=['HS256'])
            
            user_doc = current_app.db.collection('users').document(data['user_id']).get()
            if not user_doc.exists:
                return jsonify({'error': 'User not found'}), 401
                
            current_user = {'id': user_doc.id, **user_doc.to_dict()}
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

@auth.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if user exists
        users_ref = current_app.db.collection('users')
        query = users_ref.where('email', '==', data['email']).limit(1).get()
        
        if len(list(query)) > 0:
            return jsonify({'error': 'User already exists'}), 400
        
        # Create new user
        new_user = {
            'email': data['email'],
            'password': generate_password_hash(data['password']),
            'created_at': datetime.datetime.now()
        }
        
        # Add to database
        user_ref = users_ref.add(new_user)
        
        # Generate token
        token = jwt.encode({
            'user_id': user_ref[1].id,
            'email': data['email'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
        }, os.getenv('SECRET_KEY'), algorithm='HS256')
        
        return jsonify({
            'message': 'User created successfully',
            'token': token
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Find user
        users_ref = current_app.db.collection('users')
        query = users_ref.where('email', '==', data['email']).limit(1).get()
        
        user = None
        for doc in query:
            user = {'id': doc.id, **doc.to_dict()}
            break
            
        if not user or not check_password_hash(user['password'], data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate token
        token = jwt.encode({
            'user_id': user['id'],
            'email': user['email'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
        }, os.getenv('SECRET_KEY'), algorithm='HS256')
        
        return jsonify({'token': token}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500