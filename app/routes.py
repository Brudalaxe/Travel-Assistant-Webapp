'''
app/routes.py

This files handles all routing functionality for the app, including web interface routes
and API endpoints. This includes weather data, restaurant info, tourist attractions, and
user reviews, making use of the OpenWeatherMap and Geoapify APis.

Functions:

Web interface
1. index(): Renders homepage with search form
2. search_city(): Handles city search and data display
3. login_page(), register_page(): Render authentication pages

API Endpoints
1. get_weather(): Fetches weather data from OpenWeatherMap
2. get_places(): Fetches restaurant data from Geoapify
3. get_attractions(): Fetches tourist attraction data from Geoapify
4. get_reviews(), add_review(): Handle city reviews in Firestore

Error Handlers
1. not_found_error(): Handles 404 errors
2. internal_error(): Handles 500 errors
'''

from flask import Blueprint, render_template, redirect, url_for, request, jsonify, current_app
from google.cloud.firestore_v1.base_query import FieldFilter
import jwt
import requests
import datetime
from app.auth import token_required
from app.utils import validate_rating
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

main = Blueprint('main', __name__)

WEATHER_ICONS = {
    # Clear sky
    '01d': 'fa-sun',
    '01n': 'fa-moon',
    
    # Few clouds
    '02d': 'fa-cloud-sun',
    '02n': 'fa-cloud-moon',
    
    # Scattered clouds
    '03d': 'fa-cloud',
    '03n': 'fa-cloud',
    
    # Broken clouds
    '04d': 'fa-cloud',
    '04n': 'fa-cloud',
    
    # Shower rain
    '09d': 'fa-cloud-showers-heavy',
    '09n': 'fa-cloud-showers-heavy',
    
    # Rain
    '10d': 'fa-cloud-rain',
    '10n': 'fa-cloud-rain',
    
    # Thunderstorm
    '11d': 'fa-bolt',
    '11n': 'fa-bolt',
    
    # Snow
    '13d': 'fa-snowflake',
    '13n': 'fa-snowflake',
    
    # Mist
    '50d': 'fa-smog',
    '50n': 'fa-smog'
}

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
    
    try:
        # Use API endpoints instead of direct external API calls
        weather_response = requests.get(f"https://localhost:443/api/weather/{city}", verify=False)
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        # Get weather icon (this needs to be added to the weather API response)
        icon_code = '01d'
        weather = {
                'temperature': weather_data['temperature'],
                'description': weather_data['description'],
                'humidity': weather_data['humidity'],
                'pressure': weather_data['pressure'],
                'wind_speed': weather_data['wind_speed'],
                'temp_min': weather_data['temp_min'],
                'temp_max': weather_data['temp_max'],
                'visibility': weather_data['visibility'],
                'icon': WEATHER_ICONS.get(weather_data['icon'], 'fa-cloud')
            }
        
        # Get restaurants data using API endpoint
        try:
            restaurants_response = requests.get(f"https://localhost:443/api/places/{city}", verify=False)
            restaurants_response.raise_for_status()
            restaurants_data = restaurants_response.json()
            restaurants = restaurants_data.get('restaurants', [])
        except requests.exceptions.RequestException as e:
            restaurants = []
        except Exception as e:
            restaurants = []

        # Get attractions data using API endpoint
        try:
            attractions_response = requests.get(f"https://localhost:443/api/attractions/{city}", verify=False)
            if attractions_response.ok:
                attractions_data = attractions_response.json()
                attractions = attractions_data.get('attractions', [])
            else:
                attractions = []
        except Exception as e:
            print(f"Attractions error: {e}")
            attractions = []
        
        # Get reviews using API endpoint
        reviews_response = requests.get(f"https://localhost:443/api/reviews/{city}", verify=False)
        reviews = reviews_response.json() if reviews_response.ok else []
        
        # Calculate average rating
        if reviews:
            average_rating = sum(review['rating'] for review in reviews) / len(reviews)
            recent_reviews = sorted(reviews, 
                                 key=lambda x: x.get('created_at', 0), 
                                 reverse=True)[:5]
        else:
            average_rating = 0
            recent_reviews = []

        # REQUIREMENT Option 2.3: User accounts and access management

        # Check if user is logged in
        token = request.cookies.get('token')
        current_user = None
        if token:
            try:
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
                             current_user=current_user,
                             restaurants=restaurants,
                             attractions=attractions)
                             
    except Exception as e:
        print(f"Error: {str(e)}")
        return render_template('error.html', message="City not found")

# REQUIREMENT 1: REST API Implementation with proper response codes
# API Routes
@main.route('/api/weather/<city>', methods=['GET'])
def get_weather(city):
    # REQUIREMENT 2: External REST Services Integration
    api_key = os.getenv('WEATHER_API_KEY')
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()
        return jsonify({
            'temperature': round(weather_data['main']['temp'], 1),
            'description': weather_data['weather'][0]['description'],
            'humidity': weather_data['main']['humidity'],
            'pressure': weather_data['main']['pressure'],
            'wind_speed': round(weather_data['wind']['speed'], 1),
            'temp_min': round(weather_data['main']['temp_min'], 1),
            'temp_max': round(weather_data['main']['temp_max'], 1),
            'visibility': weather_data.get('visibility', 0),
            'icon': weather_data['weather'][0]['icon']
        }), 200
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'City not found'}), 404

# REQUIREMENT 1: REST API Implementation with proper response codes
@main.route('/api/places/<city>', methods=['GET'])
def get_places(city):
    # REQUIREMENT 2: External REST Services Integration
    api_key = os.getenv("PLACES_API_KEY")
    
    if not api_key:
        return jsonify({"error": "Geoapify API key not configured"}), 500

    try:
        # Step 1: Get coordinates
        geocoding_url = f"https://api.geoapify.com/v1/geocode/search?text={city}&apiKey={api_key}"
        geocoding_response = requests.get(geocoding_url)
        geocoding_data = geocoding_response.json()

        features = geocoding_data.get('features', [])
        if not features:
            return jsonify({"error": "City not found"}), 404

        lat, lon = features[0]['geometry']['coordinates'][1], features[0]['geometry']['coordinates'][0]

        # Step 2: Get restaurants
        places_url = f"https://api.geoapify.com/v2/places"
        places_params = {
            "categories": "catering.restaurant",
            "filter": f"circle:{lon},{lat},5000",  # 5 km radius
            "limit": 5,
            "sort": "popularity:desc",
            "bias": f"proximity:{lon},{lat}",
            "apiKey": api_key
        }
        places_response = requests.get(places_url, params=places_params)
        places_data = places_response.json()

        restaurants = [
            {
                "name": place['properties'].get('name', "N/A"),
                "address": f"{place['properties'].get('street', '')}, {place['properties'].get('postcode', 'N/A')}",
                "cuisine": place['properties'].get('catering', {}).get('cuisine', 'N/A'),
                "opening_hours": place['properties'].get('opening_hours', 'N/A'),
                "phone": place['properties'].get('contact', {}).get('phone', 'N/A'),
                "website": place['properties'].get('website', 'N/A')
            }
            for place in places_data.get('features', [])
        ]

        return jsonify({"city": city.title(), "restaurants": restaurants}), 200

    except Exception as e:
        return jsonify({"error": "An error occurred while fetching data"}), 500

# REQUIREMENT 1: REST API Implementation with proper response codes
@main.route('/api/attractions/<city>', methods=['GET'])
def get_attractions(city):
    # REQUIREMENT 2: External REST Services Integration
    api_key = os.getenv("PLACES_API_KEY")
    if not api_key:
        return jsonify({"error": "Geoapify API key not configured"}), 500

    try:
        # Get coordinates (same as get_places)
        geocoding_url = f"https://api.geoapify.com/v1/geocode/search?text={city}&apiKey={api_key}"
        geocoding_response = requests.get(geocoding_url)
        geocoding_data = geocoding_response.json()
        
        features = geocoding_data.get('features', [])
        if not features:
            return jsonify({"error": "City not found"}), 404

        lat, lon = features[0]['geometry']['coordinates'][1], features[0]['geometry']['coordinates'][0]

        # Get attractions
        places_url = f"https://api.geoapify.com/v2/places"
        places_params = {
            "categories": "tourism.sights,tourism.attraction,entertainment.museum,entertainment.theme_park,tourism.information.office,heritage.unesco",
            "filter": f"circle:{lon},{lat},5000",
            "limit": 5,
            "sort": "popularity:desc",
            "apiKey": api_key
        }
        
        places_response = requests.get(places_url, params=places_params)
        places_data = places_response.json()

        attractions = [
            {
                "name": place['properties'].get('name', "N/A"),
                "address": f"{place['properties'].get('street', '')}, {place['properties'].get('postcode', 'N/A')}",
                "description": place['properties'].get('description', 'N/A'),
                "website": place['properties'].get('website', 'N/A')
            }
            for place in places_data.get('features', [])
        ]

        return jsonify({"city": city.title(), "attractions": attractions}), 200

    except requests.exceptions.RequestException:
        return jsonify({"error": "An error occurred while fetching data"}), 500

# REQUIREMENT 1: REST API Implementation with proper response codes
@main.route('/api/reviews/<city>', methods=['GET'])
def get_reviews(city):
    """
    Get all reviews for a specific city
    """
    try:
        # REQUIREMENT 3: Cloud Database (Firestore) Integration
        reviews_ref = current_app.db.collection('reviews').where(filter=FieldFilter('city', '==', city)).stream()
        reviews = [doc.to_dict() for doc in reviews_ref]
        return jsonify(reviews), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# REQUIREMENT Option 2.4: Protected routes (?)

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