from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core import mail
from allauth.account.models import EmailAddress

User = get_user_model()

class AuthenticationTests(APITestCase):

    def setUp(self):
        self.register_url = reverse('rest_register')
        self.login_url = reverse('rest_login')
        self.password_change_url = reverse('rest_password_change')
        self.password_reset_url = reverse('rest_password_reset')
        
        # dj-rest-auth token refresh URL (only available if JWT is enabled and simplejwt is installed)
        self.token_refresh_url = reverse('token_refresh')

        self.user_data = {
            'email': 'testuser@example.com',
            'password': 'StrongPassword123!',
        }
        
        self.registration_data = {
            'email': 'newuser@example.com',
            'password1': 'StrongPassword123!',
            'password2': 'StrongPassword123!',
        }

    def test_user_registration(self):
        """Test user can register via API."""
        response = self.client.post(self.register_url, self.registration_data)
        if response.status_code != status.HTTP_201_CREATED:
            print("Registration payload error:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=self.registration_data['email']).exists())
        
        # Since ACCOUNT_EMAIL_VERIFICATION might be optional/mandatory,
        # we just ensure the user is created.

    def test_user_login_jwt_and_session(self):
        """Test user can log in and receives JWT cookies and sessionid."""
        # Create user via model manager to bypass registration flow for this test
        user = User.objects.create_user(email=self.user_data['email'], password=self.user_data['password'])
        EmailAddress.objects.create(user=user, email=user.email, primary=True, verified=True)

        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify JWT is in the cookies (as configured in settings.REST_AUTH)
        self.assertIn('jwt-auth', response.cookies)
        self.assertIn('jwt-refresh-token', response.cookies)
        
        # Verify Session auth is also working
        self.assertIn('sessionid', response.cookies)
        
    def test_jwt_token_refresh(self):
        """Test that the JWT refresh token can be used to get a new access token."""
        user = User.objects.create_user(email=self.user_data['email'], password=self.user_data['password'])
        EmailAddress.objects.create(user=user, email=user.email, primary=True, verified=True)
        login_response = self.client.post(self.login_url, {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        })
        
        refresh_token = login_response.cookies.get('jwt-refresh-token').value
        
        # Send the refresh token in the cookie as dj-rest-auth expects it for JWTCookieAuthentication
        self.client.cookies['jwt-refresh-token'] = refresh_token
        
        response = self.client.post(self.token_refresh_url, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return a new access token cookie
        self.assertIn('jwt-auth', response.cookies)

    def test_change_password(self):
        """Test an authenticated user can change their password."""
        user = User.objects.create_user(email=self.user_data['email'], password=self.user_data['password'])
        EmailAddress.objects.create(user=user, email=user.email, primary=True, verified=True)
        
        # Authenticate the client
        self.client.force_authenticate(user=user)
        
        change_password_data = {
            'old_password': self.user_data['password'],
            'new_password1': 'NewStrongPassword123!',
            'new_password2': 'NewStrongPassword123!',
        }
        response = self.client.post(self.password_change_url, change_password_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify password actually changed
        user.refresh_from_db()
        self.assertTrue(user.check_password('NewStrongPassword123!'))

    def test_reset_password_complete_flow(self):
        """Test the entire password reset flow from requesting an email to setting a new password."""
        user = User.objects.create_user(email=self.user_data['email'], password=self.user_data['password'])
        EmailAddress.objects.create(user=user, email=user.email, primary=True, verified=True)
        
        # 1. Request password reset
        reset_data = {'email': self.user_data['email']}
        response = self.client.post(self.password_reset_url, reset_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 2. Verify email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Password Reset', mail.outbox[0].subject)
        email_body = mail.outbox[0].body
        
        # 3. Extract uidb64 and token from the email context
        # dj-rest-auth's default email template includes the URL:
        # http://example.com/auth/password/reset/confirm/<uidb64>/<token>/
        import re
        match = re.search(r'confirm/([^/]+)/([^/]+)/', email_body)
        self.assertIsNotNone(match, "Could not extract uidb64 and token from email body")
        uidb64, token = match.groups()
        
        # 4. Confirm the password reset
        reset_confirm_url = reverse('rest_password_reset_confirm')
        confirm_data = {
            'uid': uidb64,
            'token': token,
            'new_password1': 'NewStrongPassword123!',
            'new_password2': 'NewStrongPassword123!'
        }
        confirm_response = self.client.post(reset_confirm_url, confirm_data)
        if confirm_response.status_code != status.HTTP_200_OK:
            print("Password Reset Confirm Error:", confirm_response.data)
        self.assertEqual(confirm_response.status_code, status.HTTP_200_OK)
        
        # 5. Verify the password was actually changed in the database
        user.refresh_from_db()
        self.assertTrue(user.check_password('NewStrongPassword123!'))

    def test_password_validation_rules(self):
        """Test password complexity rules during registration."""
        weak_passwords = [
            'short',  # Too short
            'alllowercase1!',  # No uppercase
            'ALLUPPERCASE1!',  # No lowercase
            'NoNumberHere!',  # No number
            'NoSymbolHere123',  # No symbol
        ]
        
        for idx, weak_pwd in enumerate(weak_passwords):
            data = {
                'email': f'weak{idx}@example.com',
                'password1': weak_pwd,
                'password2': weak_pwd,
            }
            res = self.client.post(self.register_url, data)
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST, f"Password '{weak_pwd}' should fail validation")

    def test_login_unverified_email(self):
        """Test login fails if email is not verified."""
        user = User.objects.create_user(email='unverified@example.com', password='StrongPassword123!')
        EmailAddress.objects.create(user=user, email=user.email, primary=True, verified=False)
        res = self.client.post(self.login_url, {'email': 'unverified@example.com', 'password': 'StrongPassword123!'})
        # allauth returns 400 when email is unverified
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_wrong_password(self):
        """Test login fails with incorrect password."""
        user = User.objects.create_user(email='wrongpass@example.com', password='StrongPassword123!')
        EmailAddress.objects.create(user=user, email=user.email, primary=True, verified=True)
        res = self.client.post(self.login_url, {'email': 'wrongpass@example.com', 'password': 'WrongPassword123!'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_past_password(self):
        """Test login fails with past password after it was changed."""
        user = User.objects.create_user(email='pastpass@example.com', password='StrongPassword123!')
        EmailAddress.objects.create(user=user, email=user.email, primary=True, verified=True)
        
        self.client.force_authenticate(user=user)
        self.client.post(self.password_change_url, {
            'old_password': 'StrongPassword123!',
            'new_password1': 'NewStrongPassword123!',
            'new_password2': 'NewStrongPassword123!',
        })
        self.client.logout()
        
        # Try login with old password
        res = self.client.post(self.login_url, {'email': 'pastpass@example.com', 'password': 'StrongPassword123!'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Try login with new password
        res2 = self.client.post(self.login_url, {'email': 'pastpass@example.com', 'password': 'NewStrongPassword123!'})
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
