from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.test import TestCase
from listings.models import Listing

User = get_user_model()

class BaseListingTest:
    """
    Abstract-style base class for Listing tests.
    Shared logic for creating, updating, and deleting listings.
    """
    def setUp(self):
        super().setUp()
        self.user_a = User.objects.create_user(email=f'usera_{self.__class__.__name__}@example.com', password='StrongPassword123!')
        self.user_b = User.objects.create_user(email=f'userb_{self.__class__.__name__}@example.com', password='StrongPassword123!')
        self.setup_urls()

    def setup_urls(self):
        raise NotImplementedError

    def authenticate(self, user):
        raise NotImplementedError

    def perform_create(self, data):
        raise NotImplementedError

    def perform_update(self, pk, data):
        raise NotImplementedError

    def perform_delete(self, pk):
        raise NotImplementedError

    # Assertions
    def assert_success_create(self, response):
        raise NotImplementedError

    def assert_success_update(self, response):
        raise NotImplementedError

    def assert_success_delete(self, response):
        raise NotImplementedError

    def assert_forbidden(self, response):
        raise NotImplementedError

    def assert_unauthorized(self, response):
        raise NotImplementedError

    # Shared Tests
    def test_create_listing(self):
        """Generic test for creating a listing."""
        self.authenticate(self.user_a)
        data = {'title': 'Base Item', 'description': 'Shared test', 'price': '10.00'}
        response = self.perform_create(data)
        self.assert_success_create(response)
        self.assertTrue(Listing.objects.filter(title='Base Item', seller=self.user_a).exists())

    def test_update_listing(self):
        """Generic test for updating a listing."""
        listing = Listing.objects.create(seller=self.user_a, title='Old', price='5.00')
        self.authenticate(self.user_a)
        data = {'title': 'New', 'price': '15.00'}
        response = self.perform_update(listing.id, data)
        self.assert_success_update(response)
        listing.refresh_from_db()
        self.assertEqual(listing.title, 'New')

    def test_delete_listing(self):
        """Generic test for deleting a listing."""
        listing = Listing.objects.create(seller=self.user_a, title='Bye', price='5.00')
        self.authenticate(self.user_a)
        response = self.perform_delete(listing.id)
        self.assert_success_delete(response)
        self.assertFalse(Listing.objects.filter(id=listing.id).exists())

    def test_owner_protection(self):
        """Generic test for owner protection."""
        listing = Listing.objects.create(seller=self.user_b, title='Not Mine', price='5.00')
        self.authenticate(self.user_a)
        
        # Try update
        res_upd = self.perform_update(listing.id, {'title': 'Hacked'})
        self.assert_forbidden(res_upd)
        
        # Try delete
        res_del = self.perform_delete(listing.id)
        self.assert_forbidden(res_del)
        
        listing.refresh_from_db()
        self.assertEqual(listing.title, 'Not Mine')

    def test_unauthenticated_access(self):
        """Generic test to verify unauthenticated users are blocked."""
        # Note: No self.authenticate() called here
        
        # Try Create
        res_create = self.perform_create({'title': 'No Auth'})
        self.assert_unauthorized(res_create)
        
        # Try Update
        listing = Listing.objects.create(seller=self.user_a, title='Protected', price='10.00')
        res_update = self.perform_update(listing.id, {'title': 'I am anonymous'})
        self.assert_unauthorized(res_update)
        
        # Try Delete
        res_delete = self.perform_delete(listing.id)
        self.assert_unauthorized(res_delete)

class ListingAPITests(BaseListingTest, APITestCase):
    def setup_urls(self):
        self.list_create_url = reverse('listings_api:api_listings_list')

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def perform_create(self, data):
        return self.client.post(self.list_create_url, data)

    def perform_update(self, pk, data):
        url = reverse('listings_api:api_listings_detail', kwargs={'pk': pk})
        return self.client.put(url, data)

    def perform_delete(self, pk):
        url = reverse('listings_api:api_listings_detail', kwargs={'pk': pk})
        return self.client.delete(url)

    def assert_success_create(self, response):
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def assert_success_update(self, response):
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def assert_success_delete(self, response):
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def assert_forbidden(self, response):
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def assert_unauthorized(self, response):
        # DRF returns 401 if authentication credentials are not provided, 
        # but sometimes 403 for anonymous on certain view configurations.
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

class ListingWebViewTests(BaseListingTest, TestCase):
    def setup_urls(self):
        self.index_url = reverse('listings:index')
        self.create_url = reverse('listings:create')

    def authenticate(self, user):
        self.client.force_login(user)

    def perform_create(self, data):
        return self.client.post(self.create_url, data)

    def perform_update(self, pk, data):
        url = reverse('listings:edit', kwargs={'pk': pk})
        return self.client.post(url, data)

    def perform_delete(self, pk):
        url = reverse('listings:delete', kwargs={'pk': pk})
        return self.client.post(url) # Web uses POST for deletion confirmation

    def assert_success_create(self, response):
        self.assertRedirects(response, self.index_url)

    def assert_success_update(self, response):
        self.assertRedirects(response, self.index_url)

    def assert_success_delete(self, response):
        self.assertRedirects(response, self.index_url)

    def assert_forbidden(self, response):
        self.assertEqual(response.status_code, 403)

    def assert_unauthorized(self, response):
        # Web should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('account_login'), response.url)

    # Web-specific extra test
    def test_index_view(self):
        """Test the marketplace index displays active listings."""
        Listing.objects.create(seller=self.user_a, title='Active Item', price='10.00', is_active=True)
        Listing.objects.create(seller=self.user_b, title='Inactive Item', price='10.00', is_active=False)
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Active Item')
        self.assertNotContains(response, 'Inactive Item')
