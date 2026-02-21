from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_password_change_redirect_url(self, request):
        return reverse('users:profile')

    def get_password_set_redirect_url(self, request):
        return reverse('users:profile')
