from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from . import serializers

class UserProfileAPIView(generics.RetrieveAPIView):
    """API view to fetch user profile data for mobile."""
    serializer_class = serializers.UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
from rest_framework.views import APIView
from rest_framework.response import Response
from allauth.account.forms import ResetPasswordForm

class PasswordResetAPIView(APIView):
    """
    A direct API wrapper for allauth's ResetPasswordForm.
    Bypasses dj_rest_auth's custom URL generator to ensure the mobile app
    triggers the exact same email link as the Web flow (no custom generator needed).
    """
    permission_classes = []

    def post(self, request, *args, **kwargs):
        form = ResetPasswordForm(data=request.data)
        if form.is_valid():
            # The allauth form automatically generates the native Web confirmation URL
            form.save(request)
            return Response({"detail": "Password reset e-mail has been sent."})
        return Response(form.errors, status=400)
