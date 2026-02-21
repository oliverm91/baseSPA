from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def profile_view(request):
    """View to display the user's profile and their listings."""
    # Since we set related_name="listings" on the Listing model
    user_listings = request.user.listings.all().order_by('-created_at')
    
    context = {
        'user_listings': user_listings
    }
    return render(request, "users/profile.html", context)
