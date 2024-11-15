# app/routes.py
from flask import Blueprint, jsonify, request, current_app
import requests
from app.auth import token_required
from app.utils import validate_rating
import os

main = Blueprint('main', __name__)

@main.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Welcome to the Travel Assistant API',
        'endpoints': {
            'weather': '/api/weather/<city>',
            'reviews': '/api/reviews/<city>',
            'auth': {
                'register': '/api/register',
                'login': '/api/login'
            }
        }
    }), 200

@main.route('/api/weather/<city>', methods=['GET'])
def get_weather(city):
    """
    Get weather information for a specific city using OpenWeatherMap API
    """
    api_key = os.getenv('WEATHER_API_KEY')
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()
        return jsonify({
            'temperature': weather_data['main']['temp'],
            'description': weather_data['weather'][0]['description'],
            'humidity': weather_data['main']['humidity']
        }), 200
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'City not found'}), 404

@main.route('/api/reviews/<city>', methods=['GET'])
def get_reviews(city):
    """
    Get all reviews for a specific city
    """
    try:
        reviews_ref = current_app.db.collection('reviews').where('city', '==', city).stream()
        reviews = [doc.to_dict() for doc in reviews_ref]
        return jsonify(reviews), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/api/reviews/<city>', methods=['POST'])
@token_required
def add_review(current_user, city):
    """
    Add a new review for a city
    """
    try:
        data = request.get_json()
        if not validate_rating(data.get('rating')):
            return jsonify({'error': 'Invalid rating'}), 400

        review = {
            'city': city,
            'rating': data['rating'],
            'comment': data.get('comment', ''),
            'user_id': current_user['id'],
            'username': current_user['email']
        }
        
        current_app.db.collection('reviews').add(review)
        return jsonify({'message': 'Review added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500