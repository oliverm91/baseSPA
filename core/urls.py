from django.contrib import admin
from django.urls import path, include
from . import views
from listings.urls import web_urlpatterns as listings_web_urls, api_urlpatterns as listings_api_urls
from users.urls import web_urlpatterns as users_web_urls, api_urlpatterns as users_api_urls
from users.api_views import PasswordResetAPIView

urlpatterns = [
    # Global Landing
    path('', views.landing_page, name='landing'),
    path('admin/', admin.site.urls),
    
    # ==================
    # AUTHENTICATION
    # ==================
    
    # Actually, dj_rest_auth.urls includes /user/ which user wanted to block maybe? 
    # Let's be fully explicit for dj_rest_auth API:
    path('auth/login/', __import__('dj_rest_auth.views').views.LoginView.as_view(), name='rest_login'),
    path('auth/logout/', __import__('dj_rest_auth.views').views.LogoutView.as_view(), name='rest_logout'),
    path('auth/password/change/', __import__('dj_rest_auth.views').views.PasswordChangeView.as_view(), name='rest_password_change'),
    path('auth/password/reset/', PasswordResetAPIView.as_view(), name='rest_password_reset'),
    path('auth/registration/', __import__('dj_rest_auth.registration.views').registration.views.RegisterView.as_view(), name='rest_register'),
    path('auth/token/refresh/', __import__('dj_rest_auth.jwt_auth').jwt_auth.get_refresh_view().as_view(), name='token_refresh'),
    path('auth/token/verify/', __import__('rest_framework_simplejwt.views').views.TokenVerifyView.as_view(), name='token_verify'),

    # 2. Web Endpoints (allauth core)
    path('accounts/login/', __import__('allauth.account.views').account.views.login, name='account_login'),
    path('accounts/signup/', __import__('allauth.account.views').account.views.signup, name='account_signup'),
    path('accounts/logout/', __import__('allauth.account.views').account.views.logout, name='account_logout'),
    
    path('accounts/password/change/', __import__('allauth.account.views').account.views.password_change, name='account_change_password'),
    path('accounts/password/set/', __import__('allauth.account.views').account.views.password_set, name='account_set_password'),
    path('accounts/password/reset/', __import__('allauth.account.views').account.views.password_reset, name='account_reset_password'),
    path('accounts/password/reset/done/', __import__('allauth.account.views').account.views.password_reset_done, name='account_reset_password_done'),
    path('accounts/password/reset/key/<uidb36>-<key>/', __import__('allauth.account.views').account.views.password_reset_from_key, name='account_reset_password_from_key'),
    path('accounts/password/reset/key/done/', __import__('allauth.account.views').account.views.password_reset_from_key_done, name='account_reset_password_from_key_done'),

    path('accounts/confirm-email/', __import__('allauth.account.views').account.views.email_verification_sent, name='account_email_verification_sent'),
    path('accounts/confirm-email/<key>/', __import__('allauth.account.views').account.views.confirm_email, name='account_confirm_email'),

    # 3. Google OAuth Endpoints (allauth socialaccount)
    path('accounts/', include('allauth.socialaccount.providers.google.urls')),

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
