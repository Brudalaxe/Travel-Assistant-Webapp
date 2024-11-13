# app/utils.py
def validate_rating(rating):
    """
    Validate that the rating is between 1 and 5
    """
    try:
        rating = float(rating)
        return 1 <= rating <= 5
    except:
        return False
