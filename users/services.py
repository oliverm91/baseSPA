from django.contrib.auth import get_user_model

User = get_user_model()

def get_user_profile_data(user):
    """
    Returns a dictionary of profile data for the given user.
    Includes user info and their listings.
    """
    # In a more complex app, this might include stats, badges, etc.
    return {
        'user': user,
        'listings': user.listings.all().order_by('-created_at')
    }
