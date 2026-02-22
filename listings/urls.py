from django.urls import path
from . import views, api_views

app_name = 'listings'

# For web-exclusive HTML views
web_urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_listing_view, name='create'),
    path('<int:pk>/edit/', views.edit_listing_view, name='edit'),
    path('<int:pk>/delete/', views.delete_listing_view, name='delete'),
]

# For mobile-exclusive JSON API
api_urlpatterns = [
    path('', api_views.ListingListView.as_view(), name='api_listings_list'),
    path('<int:pk>/', api_views.ListingDetailView.as_view(), name='api_listings_detail'),
]

# Legacy combined pattern
urlpatterns = web_urlpatterns + api_urlpatterns
