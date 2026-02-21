from django.urls import path
from . import views
from . import api_views

app_name = 'listings'

urlpatterns = [
    # Web views (HTML)
    path('', views.index, name='index'),
    path('create/', views.create_listing_view, name='create'),
    path('<int:pk>/edit/', views.edit_listing_view, name='edit'),
    path('<int:pk>/delete/', views.delete_listing_view, name='delete'),
    
    # API endpoints (JSON)
    path('api/listings/', api_views.ListingListView.as_view(), name='api_listings_list'),
    path('api/listings/<int:pk>/', api_views.ListingDetailView.as_view(), name='api_listings_detail'),
]
