from django.contrib.auth import get_user_model
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from rest_framework import serializers
from allauth.account.adapter import get_adapter
from allauth.account import app_settings as allauth_settings
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class CustomRegisterSerializer(RegisterSerializer):
    username = None

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and User.objects.filter(email__iexact=email).exists():
                raise serializers.ValidationError(
                    _("A user is already registered with this e-mail address.")
                )
        return email

class CustomLoginSerializer(LoginSerializer):
    def validate(self, attrs):
        attrs = super().validate(attrs)
        user = attrs.get('user') or self.user
        
        if user and hasattr(user, 'emailaddress_set'):
            email_address = user.emailaddress_set.filter(email=user.email, verified=True).first()
            if not email_address:
                raise serializers.ValidationError("E-mail is not verified.")
                
        return attrs

class UserListingSerializer(serializers.Serializer):
    """Simplified listing serializer for profile view."""
    id = serializers.IntegerField()
    title = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    created_at = serializers.DateTimeField()

class UserProfileSerializer(serializers.ModelSerializer):
    listings = UserListingSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'listings']
