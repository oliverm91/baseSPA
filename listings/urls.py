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
    path('', api_views.ListingListAPIView.as_view(), name='api_listings_list'),
    path('create/', api_views.ListingCreateAPIView.as_view(), name='api_listings_create'),
    path('<int:pk>/', api_views.ListingDetailAPIView.as_view(), name='api_listings_detail'),
    path('<int:pk>/edit/', api_views.ListingEditAPIView.as_view(), name='api_listings_edit'),
    path('<int:pk>/delete/', api_views.ListingDeleteAPIView.as_view(), name='api_listings_delete'),
]

# Legacy combined pattern
urlpatterns = web_urlpatterns + api_urlpatterns
