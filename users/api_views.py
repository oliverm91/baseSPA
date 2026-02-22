from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from . import serializers

class UserProfileAPIView(generics.RetrieveAPIView):
    """API view to fetch user profile data for mobile."""
    serializer_class = serializers.UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
