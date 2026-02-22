from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

User = get_user_model()

def get_user_profile_data(user):
    """
    Returns a dictionary of profile data for the given user.
    Includes user info and their listings.
    """
    if not user or not user.is_authenticated:
        raise PermissionDenied("Authentication is required to access user profile data.")
    # In a more complex app, this might include stats, badges, etc.
    return {
        'user': user,
        'listings': user.listings.all().order_by('-created_at')
    }
