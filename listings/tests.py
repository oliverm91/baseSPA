from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from listings.models import Listing

User = get_user_model()

class ListingAPITests(APITestCase):

    def setUp(self):
        self.user_a = User.objects.create_user(email='usera@example.com', password='StrongPassword123!')
        self.user_b = User.objects.create_user(email='userb@example.com', password='StrongPassword123!')
        
        self.list_create_url = reverse('listings:api_listings_list')

    def test_create_listing(self):
        """Test authenticated user can create a listing."""
        self.client.force_authenticate(user=self.user_a)
        data = {
            'title': 'Test Item',
            'description': 'A nice test item',
            'price': '10.50'
        }
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Listing.objects.filter(title='Test Item', seller=self.user_a).exists())

    def test_update_listing(self):
        """Test user can modify their own listing."""
        listing = Listing.objects.create(seller=self.user_a, title='Old Title', description='Old', price='5.00')
        detail_url = reverse('listings:api_listings_detail', kwargs={'pk': listing.id})
        
        self.client.force_authenticate(user=self.user_a)
        data = {
            'title': 'New Title',
            'price': '15.00'
        }
        response = self.client.put(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        listing.refresh_from_db()
        self.assertEqual(listing.title, 'New Title')
        self.assertEqual(listing.price, 15.00)

    def test_delete_listing(self):
        """Test user can delete their own listing."""
        listing = Listing.objects.create(seller=self.user_a, title='To Delete', description='Old', price='5.00')
        detail_url = reverse('listings:api_listings_detail', kwargs={'pk': listing.id})
        
        self.client.force_authenticate(user=self.user_a)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Listing.objects.filter(id=listing.id).exists())

    def test_user_a_cannot_modify_user_b_listing(self):
        """Test cross-user modification protection."""
        listing = Listing.objects.create(seller=self.user_b, title='User B Item', description='Old', price='5.00')
        detail_url = reverse('listings:api_listings_detail', kwargs={'pk': listing.id})
        
        # Authenticate as User A
        self.client.force_authenticate(user=self.user_a)
        data = {
            'title': 'Hacked Title'
        }
        response = self.client.put(detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        listing.refresh_from_db()
        self.assertEqual(listing.title, 'User B Item')

    def test_user_a_cannot_delete_user_b_listing(self):
        """Test cross-user deletion protection."""
        listing = Listing.objects.create(seller=self.user_b, title='User B Item', description='Old', price='5.00')
        detail_url = reverse('listings:api_listings_detail', kwargs={'pk': listing.id})
        
        # Authenticate as User A
        self.client.force_authenticate(user=self.user_a)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        self.assertTrue(Listing.objects.filter(id=listing.id).exists())
