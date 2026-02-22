from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from . import serializers, services

class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Returns the authenticated user's profile and listings."""
        profile_data = services.get_user_profile_data(request.user)
        # We wrap the user object in the data returned by service to match the serializer
        serializer = serializers.UserProfileSerializer(request.user)
        return Response(serializer.data)
