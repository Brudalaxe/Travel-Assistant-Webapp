# Travel Assistant

[![Travel Assistant Demo](https://img.youtube.com/vi/wlcbZZvOrsw/maxresdefault.jpg)](https://www.youtube.com/watch?v=wlcbZZvOrsw)

A Flask-based REST API that provides weather information and city reviews. Users can search for cities to view current weather conditions and read or submit reviews.

## Features

- Weather information for cities using OpenWeatherMap API
- User authentication system
- City reviews with ratings and comments
- Google Cloud Firestore integration for data storage
- Responsive web interface

## Prerequisites

Before you begin, you'll need:
- Python 3.8 or higher
- Git

## Setup

1. Clone and navigate to the repository:
```bash
git clone https://github.com/Brudalaxe/Travel-Assistant-Webapp.git
cd Travel-Assistant-Webapp
```

2. Create a virtual environment and activate it:

Linux/macOS:
```bash
python -m venv env
source env/bin/activate
```

Windows:
```bash
python -m venv env
env\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Make sure your virtual environment is activated
2. Start the Flask application:
```bash
python run.py
```
3. Visit the link that is provided in the terminal

## Using the Web Interface

1. **View Weather:**
   - Enter a city name in the search box (e.g., "London")
   - Click "Search" to view current weather conditions

2. **User Registration/Login:**
   - Click "Register" to create a new account
   - Enter email
   - Enter password
     
3. **Adding Reviews:**
   - Search for a city
   - Click "Add Review"
   - Select a rating (1-5 stars)
   - Write your comment
   - Click "Submit"

## API Endpoints

### Weather
- `GET /api/weather/<city>` - Get weather information for a specific city
  
### Places
- `GET /api/places/<city>` - Get restaurant information for a specific city

### Attractions
- `GET /api/attractions/<city>` - Get tourist attractions for a specific city.

### Reviews
- `GET /api/reviews/<city>` - Get all reviews for a specific city
- `POST /api/reviews/<city>` - Add a new review (requires authentication)

### Authentication
- `POST /api/register` - Register a new user
- `POST /api/login` - Login and receive JWT token

## Project Structure

```
CCGroup2/
├── app/
│   ├── __init__.py      # Application factory and configuration
│   ├── routes.py        # Main route handlers
│   ├── auth.py          # Authentication logic
│   └── utils.py         # Utility functions
├── templates/           # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── city.html
│   ├── error.html
│   ├── login.html
│   └── register.html
├── .env                 # Environment variables
├── requirements.txt     # Project dependencies
└── run.py               # Application entry point
```
