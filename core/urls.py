from django.contrib import admin
from django.urls import path, include
from . import views
from listings.urls import web_urlpatterns as listings_web_urls, api_urlpatterns as listings_api_urls
from users.urls import web_urlpatterns as users_web_urls, api_urlpatterns as users_api_urls

urlpatterns = [
    # Global Landing
    path('', views.landing_page, name='landing'),
    path('admin/', admin.site.urls),
    
    # Auth (Shared between Web and Mobile)
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('accounts/', include('allauth.urls')),
    path('auth/password/reset/confirm/<uidb64>/<token>/', views.landing_page, name='password_reset_confirm'),

    # Web-Exclusive Views (HTML)
    path('web/', include([
        path('marketplace/', include((listings_web_urls, 'listings'))),
        path('profile/', include((users_web_urls, 'users'))),
    ])),

    # Mobile-Exclusive API Consolidated (/api/)
    path('api/', include([
        path('marketplace/', include((listings_api_urls, 'listings_api'))),
        path('profile/', include((users_api_urls, 'users_api'))),
    ])),
]
