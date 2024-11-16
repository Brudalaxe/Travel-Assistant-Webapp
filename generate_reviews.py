from google.cloud import firestore
import random
import datetime
from faker import Faker
import os
from dotenv import load_dotenv

load_dotenv()

db = firestore.Client()

fake = Faker()

cities = [
    # Top Global Cities
    'Paris', 'Dubai', 'Madrid', 'Tokyo', 'Amsterdam',
    'Berlin', 'Rome', 'New York', 'Barcelona', 'London',
    'Singapore', 'Munich', 'Milan', 'Seoul', 'Dublin',
    'Osaka', 'Hong Kong', 'Vienna', 'Los Angeles', 'Lisbon',
    
    # Major Tourist Destinations
    'Bangkok', 'Istanbul', 'Kuala Lumpur', 'Prague', 'Venice',
    'Florence', 'Budapest', 'Moscow', 'Sydney', 'Miami',
    'Las Vegas', 'San Francisco', 'Chicago', 'Toronto', 'Vancouver',
    
    # Historical Cities
    'Athens', 'Cairo', 'Jerusalem', 'Beijing', 'Kyoto',
    'Edinburgh', 'Stockholm', 'Copenhagen', 'Brussels', 'Vienna',
    'Krakow', 'St Petersburg', 'Porto', 'Granada', 'Seville',
    
    # Modern Metropolises
    'Shanghai', 'Seoul', 'Dubai', 'Singapore', 'Taipei',
    'Mumbai', 'Delhi', 'Melbourne', 'Montreal', 'Boston',
    'Seattle', 'Austin', 'Denver', 'Portland', 'San Diego',
    
    # Cultural Capitals
    'Mexico City', 'Rio de Janeiro', 'Buenos Aires', 'Lima', 'Santiago',
    'Cape Town', 'Marrakech', 'Istanbul', 'Dublin', 'Manchester',
    'Hamburg', 'Lyon', 'Marseille', 'Naples', 'Turin',
    
    # Asian Cities
    'Bangkok', 'Ho Chi Minh City', 'Jakarta', 'Manila', 'Hanoi',
    'Kuala Lumpur', 'Bali', 'Phuket', 'Chiang Mai', 'Kyoto',
    'Osaka', 'Busan', 'Taipei', 'Shanghai', 'Guangzhou',
    
    # European Cities
    'Warsaw', 'Prague', 'Budapest', 'Zagreb', 'Belgrade',
    'Bucharest', 'Sofia', 'Riga', 'Tallinn', 'Helsinki',
    'Oslo', 'Geneva', 'Zurich', 'Valencia', 'Porto',
    
    # Additional Notable Cities
    'Vancouver', 'Toronto', 'Montreal', 'Quebec City', 'Ottawa',
    'Dubai', 'Abu Dhabi', 'Doha', 'Kuwait City', 'Tel Aviv'
]

review_templates = [
    # Positive Experiences
    "Beautiful city with {feature}. {comment}",
    "Really enjoyed the {feature}. {comment}",
    "Great experience overall. {feature}. {comment}",
    "Wonderful place to visit. {feature}. {comment}",
    "Amazing destination! {feature}. {comment}",
    
    # Cultural Experiences
    "Fell in love with the {feature}. {comment}",
    "The {feature} exceeded my expectations. {comment}",
    "Such a culturally rich city with {feature}. {comment}",
    "Was impressed by the {feature}. {comment}",
    "Couldn't get enough of the {feature}. {comment}",
    
    # Travel Recommendations
    "A must-visit city with incredible {feature}. {comment}",
    "Highly recommend visiting for the {feature}. {comment}",
    "Don't miss the {feature} when you visit. {comment}",
    "The highlight was definitely the {feature}. {comment}",
    "Worth visiting just for the {feature}. {comment}",
    
    # Personal Experiences
    "Spent days exploring the {feature}. {comment}",
    "Made unforgettable memories enjoying the {feature}. {comment}",
    "Had an amazing time experiencing the {feature}. {comment}",
    "The {feature} made our trip special. {comment}",
    "We were blown away by the {feature}. {comment}",
    
    # Detailed Observations
    "The city's {feature} is world-class. {comment}",
    "Particularly impressed with the {feature}. {comment}",
    "The {feature} adds so much character to the city. {comment}",
    "You can't beat the {feature} here. {comment}",
    "The city is famous for its {feature} for good reason. {comment}",
    
    # Travel Tips
    "Pro tip: Make time for the {feature}. {comment}",
    "Best decision was exploring the {feature}. {comment}",
    "Make sure to check out the {feature}. {comment}",
    "The {feature} alone makes it worth visiting. {comment}",
    "Perfect destination if you love {feature}. {comment}"
]

features = [
    # Architecture & Landmarks
    "stunning architecture",
    "historic buildings",
    "iconic landmarks",
    "beautiful monuments",
    "ancient ruins",
    
    # Culture & Entertainment
    "vibrant culture",
    "amazing museums",
    "art galleries",
    "street performances",
    "music scene",
    "theater district",
    "nightlife",
    
    # Food & Dining
    "fantastic food scene",
    "local cuisine",
    "street food",
    "food markets",
    "traditional restaurants",
    
    # Urban Features
    "efficient public transport",
    "beautiful parks",
    "clean streets",
    "modern infrastructure",
    "shopping districts",
    
    # People & Atmosphere
    "friendly locals",
    "welcoming atmosphere",
    "diverse population",
    "cultural diversity",
    "safe environment",
    
    # Natural Elements
    "beautiful beaches",
    "scenic views",
    "natural landscapes",
    "waterfront areas",
    "green spaces"
]

positive_comments = [
    # General Positive
    "Would definitely visit again!",
    "Highly recommend to everyone.",
    "Can't wait to return.",
    "A must-visit destination.",
    "Exceeded all expectations.",
    
    # Experience-Based
    "Had an unforgettable experience.",
    "Made wonderful memories here.",
    "Perfect for any traveler.",
    "Left with amazing experiences.",
    "Everything a tourist could want.",
    
    # Specific Praise
    "The perfect city break destination.",
    "Great value for money.",
    "Something for everyone here.",
    "Absolutely worth the trip.",
    "A photographer's paradise.",
    
    # Personal Reactions
    "Fell in love with this place.",
    "Already planning my next visit.",
    "Wish I could have stayed longer.",
    "Best city I've visited so far.",
    "Exactly what we were looking for."
]

def generate_review():
    feature = random.choice(features)
    comment = random.choice(positive_comments)
    template = random.choice(review_templates)
    return template.format(feature=feature, comment=comment)

def add_reviews_to_db():
    reviews_added = 0
    
    for city in cities:
        num_reviews = random.randint(5, 10)
        
        for _ in range(num_reviews):
            review = {
                'city': city,
                'rating': random.randint(3, 5),
                'comment': generate_review(),
                'username': fake.name(),
                'user_id': fake.uuid4(),
                'created_at': datetime.datetime.now().timestamp() - random.randint(0, 30*24*60*60)
            }
            
            db.collection('reviews').add(review)
            reviews_added += 1
            
        print(f"Added {num_reviews} reviews for {city}")
    
    return reviews_added

def clear_existing_reviews():
    reviews_ref = db.collection('reviews')
    docs = reviews_ref.stream()
    for doc in docs:
        doc.reference.delete()
    print("Cleared existing reviews")

if __name__ == "__main__":
    clear_existing_reviews()
    total_reviews = add_reviews_to_db()
    print(f"\nTotal reviews added: {total_reviews}")