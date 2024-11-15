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
    'London', 'Paris', 'New York', 'Tokyo', 'Sydney', 
    'Rome', 'Barcelona', 'Berlin', 'Amsterdam', 'Dubai'
]

review_templates = [
    "Beautiful city with {feature}. {comment}",
    "Really enjoyed the {feature}. {comment}",
    "Great experience overall. {feature}. {comment}",
    "Wonderful place to visit. {feature}. {comment}",
    "Amazing destination! {feature}. {comment}"
]

features = [
    "amazing architecture",
    "fantastic food scene",
    "friendly locals",
    "excellent public transport",
    "beautiful parks",
    "rich cultural heritage",
    "vibrant nightlife",
    "stunning views",
    "historic landmarks",
    "great shopping districts"
]

positive_comments = [
    "Would definitely visit again",
    "Highly recommend",
    "Can't wait to return",
    "A must-visit destination",
    "Exceeded expectations",
    "Perfect for tourists",
    "Worth every penny",
    "Left with great memories",
    "An unforgettable experience",
    "Everything a traveler could want"
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