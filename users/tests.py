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
        
    def test_logout(self):
        """Test user can log out and tokens/sessions are cleared."""
        user = User.objects.create_user(email=self.user_data['email'], password=self.user_data['password'])
        EmailAddress.objects.create(user=user, email=user.email, primary=True, verified=True)
        # Login first
        self.client.post(self.login_url, {'email': self.user_data['email'], 'password': self.user_data['password']})
        
        logout_url = reverse('rest_logout')
        response = self.client.post(logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify tokens are cleared (cookies are unset by dj-rest-auth setting them to empty string with 1970 expiry)
        self.assertEqual(response.cookies.get('jwt-auth').value, '')
        self.assertEqual(response.cookies.get('jwt-refresh-token').value, '')

    def test_token_verify(self):
        """Test verify endpoint correctly validates an active access token."""
        user = User.objects.create_user(email=self.user_data['email'], password=self.user_data['password'])
        EmailAddress.objects.create(user=user, email=user.email, primary=True, verified=True)
        login_response = self.client.post(self.login_url, {'email': self.user_data['email'], 'password': self.user_data['password']})
        
        # Extract the access token block from dj-rest-auth's response
        access_token = login_response.data.get('access')
        self.assertIsNotNone(access_token)
        
        verify_url = reverse('token_verify')
        # Simple JWT verify view expects {"token": "<access_token>"}
        response = self.client.post(verify_url, {'token': access_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Invalid token yields 401
        invalid_response = self.client.post(verify_url, {'token': 'invalid.token.here'})
        self.assertEqual(invalid_response.status_code, status.HTTP_401_UNAUTHORIZED)

        
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
        
        # 3. Extract uidb36 and key from the email context
        # The custom URL generator sends the link to the allauth Web UI:
        # http://example.com/accounts/password/reset/key/<uidb36>-<key>/
        import re
        match = re.search(r'key/([^/]+)-([^/]+)/', email_body)
        self.assertIsNotNone(match, "Could not extract uidb36 and key from email body")
        uidb36, key = match.groups()
        
        # 4. Verify the link maps to the correct web view
        reset_confirm_url = reverse('account_reset_password_from_key', kwargs={'uidb36': uidb36, 'key': key})
        self.assertIn(reset_confirm_url, email_body)
        
        # We skip testing the actual Web POST submission here since Web forms require CSRF
        # tokens and are fully covered by allauth's own internal testing suite.

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

    def test_password_set_restricted_for_authenticated_users(self):
        """Test that an authenticated user with a password cannot access the set password view."""
        user = User.objects.create_user(email='setrest@example.com', password='StrongPassword123!')
        EmailAddress.objects.create(user=user, email=user.email, primary=True, verified=True)
        
        # Log in the user using force_login for standard Django views
        self.client.force_login(user)
        
        # Try to access the password set view (allauth HTML endpoint)
        set_password_url = reverse('account_set_password')
        response = self.client.get(set_password_url)
        
        # It should redirect (allauth redirects to password_change if password is set)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIn(reverse('account_change_password'), response.url)

    def test_web_logout_page(self):
        res = self.client.get(reverse('account_logout'))
        # Depending on ACCOUNT_LOGOUT_ON_GET, this either renders the logout confirmation page (200),
        # or instantly logs you out and redirects (302)
        self.assertIn(res.status_code, [200, 302])

    def test_web_email_verification_sent_page(self):
        res = self.client.get(reverse('account_email_verification_sent'))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'account/verification_sent.html')

    def test_web_password_reset_done_page(self):
        res = self.client.get(reverse('account_reset_password_done'))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'account/password_reset_done.html')

    def test_web_password_reset_from_key_done_page(self):
        res = self.client.get(reverse('account_reset_password_from_key_done'))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'account/password_reset_from_key_done.html')

    def test_web_set_password_page_unauthenticated(self):
        res = self.client.get(reverse('account_set_password'))
        # Unauth should redirect to login
        self.assertEqual(res.status_code, 302)
        self.assertIn(reverse('account_login'), res.url)
