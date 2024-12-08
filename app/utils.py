'''
app/utils.py

This file contains utility functions used across the app.

Functions:
1. validate_rating(): Validates that a given rating is a number between 1 and 5
'''
def validate_rating(rating):
    """
    Validate that the rating is between 1 and 5
    """
    try:
        rating = float(rating)
        return 1 <= rating <= 5
    except:
        return False
