from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from . import services

@login_required
def profile_view(request):
    """View to display the user's profile and their listings."""
    profile_data = services.get_user_profile_data(request.user)
    
    context = {
        'user_listings': profile_data['listings']
    }
    return render(request, "users/profile.html", context)
