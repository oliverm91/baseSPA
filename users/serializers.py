from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from rest_framework import serializers

class CustomRegisterSerializer(RegisterSerializer):
    username = None

class CustomLoginSerializer(LoginSerializer):
    def validate(self, attrs):
        attrs = super().validate(attrs)
        user = attrs.get('user') or self.user
        
        if user and hasattr(user, 'emailaddress_set'):
            email_address = user.emailaddress_set.filter(email=user.email, verified=True).first()
            if not email_address:
                raise serializers.ValidationError("E-mail is not verified.")
                
        return attrs
