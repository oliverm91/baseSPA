from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from . import services
from .models import Listing

def index(request):
    """HTML View to display all active listings."""
    listings = services.get_active_listings()
    return render(request, "listings/index.html", {"listings": listings})

@login_required
def create_listing_view(request):
    """HTML View to create a new listing via a form submission."""
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        price = request.POST.get("price")
        
        try:
            services.create_listing(
                seller=request.user,
                title=title,
                description=description,
                price=price
            )
            return redirect("listings:index")
        except ValueError as e:
            return render(request, "listings/create.html", {"error": str(e)})

    return render(request, "listings/create.html")

@login_required
def edit_listing_view(request, pk):
    """HTML View to edit an existing listing."""
    listing = get_object_or_404(Listing, pk=pk)
    if listing.seller != request.user:
        raise PermissionDenied

    if request.method == "POST":
        try:
            services.update_listing(
                user=request.user,
                listing_id=pk,
                title=request.POST.get("title"),
                description=request.POST.get("description"),
                price=request.POST.get("price"),
            )
            return redirect("listings:index")
        except (ValueError, PermissionDenied) as e:
            return render(request, "listings/edit.html", {"listing": listing, "error": str(e)})

    return render(request, "listings/edit.html", {"listing": listing})

@login_required
def delete_listing_view(request, pk):
    """HTML View to confirm and delete a listing."""
    listing = get_object_or_404(Listing, pk=pk)
    if listing.seller != request.user:
        raise PermissionDenied

    if request.method == "POST":
        services.delete_listing(user=request.user, listing_id=pk)
        return redirect("listings:index")

    return render(request, "listings/delete_confirm.html", {"listing": listing})
