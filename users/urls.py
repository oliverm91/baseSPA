from django.urls import path
from . import views, api_views

app_name = 'users'

# For web-exclusive HTML views
web_urlpatterns = [
    path('', views.profile_view, name='profile'),
]

# For mobile-exclusive JSON API
api_urlpatterns = [
    path('', api_views.UserProfileAPIView.as_view(), name='api_profile'),
]

# Legacy combined pattern
urlpatterns = web_urlpatterns + api_urlpatterns
