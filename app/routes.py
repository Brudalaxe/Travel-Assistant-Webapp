from flask import Blueprint, render_template, redirect, url_for, request, jsonify, current_app
import requests
import datetime
from app.auth import token_required
from app.utils import validate_rating
import os

main = Blueprint('main', __name__)

# Web Interface Routes
@main.route('/')
def index():
    """Homepage with search form"""
    return render_template('index.html')

@main.route('/search')
def search_city():
    city = request.args.get('city')
    if not city:
        return redirect(url_for('main.index'))
    
    # Get weather data
    api_key = os.getenv('WEATHER_API_KEY')
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    try:
        weather_response = requests.get(weather_url)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        
        weather = {
            'temperature': round(weather_data['main']['temp'], 1),
            'description': weather_data['weather'][0]['description'],
            'humidity': weather_data['main']['humidity'],
            'pressure': weather_data['main']['pressure'],
            'wind_speed': round(weather_data['wind']['speed'], 1),
            'temp_min': round(weather_data['main']['temp_min'], 1),
            'temp_max': round(weather_data['main']['temp_max'], 1),
            'visibility': weather_data.get('visibility', 0),
            'icon': weather_data['weather'][0]['icon']
        }
        
        # Get reviews
        reviews_ref = current_app.db.collection('reviews').where('city', '==', city).stream()
        reviews = list([doc.to_dict() for doc in reviews_ref])
        
        # Calculate average rating
        if reviews:
            average_rating = sum(review['rating'] for review in reviews) / len(reviews)
            recent_reviews = sorted(reviews, 
                                 key=lambda x: x.get('created_at', 0), 
                                 reverse=True)[:5]
        else:
            average_rating = 0
            recent_reviews = []

        # Check if user is logged in
        token = request.cookies.get('token')
        current_user = None
        if token:
            try:
                # Verify token and get user info
                data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
                current_user = {'id': data['user_id']}
            except:
                current_user = None
        
        return render_template('city.html', 
                             city=city.title(), 
                             weather=weather, 
                             reviews=reviews,
                             recent_reviews=recent_reviews,
                             average_rating=average_rating,
                             current_user=current_user)
    
    except requests.exceptions.RequestException:
        return render_template('error.html', message="City not found")

# API Routes
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
    """Add a new review for a city"""
    try:
        data = request.get_json()
        if not validate_rating(data.get('rating')):
            return jsonify({'error': 'Invalid rating'}), 400

        review = {
            'city': city,
            'rating': data['rating'],
            'comment': data.get('comment', ''),
            'user_id': current_user['id'],
            'username': current_user['email'],
            'created_at': datetime.datetime.now().timestamp()
        }
        
        # Add review to database
        current_app.db.collection('reviews').add(review)
        
        # Return the newly created review
        return jsonify({
            'message': 'Review added successfully',
            'review': review
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@main.route('/login')
def login_page():
    return render_template('login.html')

@main.route('/register')
def register_page():
    return render_template('register.html')

# Error handlers
@main.errorhandler(404)
def not_found_error(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Resource not found'}), 404
    return render_template('error.html', message="Page not found"), 404

@main.errorhandler(500)
def internal_error(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('error.html', message="An error occurred"), 500