from .models import Listing
from django.core.exceptions import PermissionDenied


def get_active_listings():
    """Returns all currently active listings ordered by creation date."""
    return Listing.objects.filter(is_active=True).select_related('seller').order_by('-created_at')

def create_listing(seller, title, description, price):
    """Creates a new listing with the given seller and details."""
    if not seller or not seller.is_authenticated:
        raise PermissionDenied("Authentication is required to create a listing.")
        
    if float(price) <= 0:
        raise ValueError("Price must be greater than zero.")
    
    listing = Listing.objects.create(
        seller=seller,
        title=title,
        description=description,
        price=price
    )
    return listing

def get_listing_by_id(listing_id):
    """Fetches a specific listing by its ID."""
    return Listing.objects.filter(id=listing_id).select_related('seller').first()

def update_listing(user, listing_id, title=None, description=None, price=None):
    """Updates a listing only if the user is the seller."""
    if not user or not user.is_authenticated:
        raise PermissionDenied("Authentication is required to modify a listing.")
        
    listing = get_listing_by_id(listing_id)
    if not listing:
        raise ValueError("Listing not found.")
    
    if listing.seller != user:
        raise PermissionDenied("You are not authorized to modify this listing.")

    if title is not None:
        listing.title = title
    if description is not None:
        listing.description = description
    if price is not None:
        if float(price) <= 0:
            raise ValueError("Price must be greater than zero.")
        listing.price = price
        
    listing.save()
    return listing

def delete_listing(user, listing_id):
    """Deletes a listing only if the user is the seller."""
    if not user or not user.is_authenticated:
        raise PermissionDenied("Authentication is required to delete a listing.")
        
    listing = get_listing_by_id(listing_id)
    if not listing:
        raise ValueError("Listing not found.")
        
    if listing.seller != user:
        raise PermissionDenied("You are not authorized to delete this listing.")
        
    listing.delete()
    return True
