from django.shortcuts import render


def landing_page(request):
    """View for the public home/landing page."""
    return render(request, "core/landing.html")
