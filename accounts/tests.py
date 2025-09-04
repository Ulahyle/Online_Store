from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from accounts.models import Customer, Address


class AccountTests(APITestCase):
    def setUp(self):
        # this method is run before each test.
        self.customer = Customer.objects.create_user(
            username='testuser', 
            password='testpassword123',
            email='test@example.com'
        )
        self.address_data = {
            "label": "Home",
            "line1": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "postal_code": "12345",
            "country": "USA"
        }

    def test_customer_registration(self):
        """
        Ensure a new customer can be registered.
        """
        url = reverse('register')
        data = {
            'username': 'newuser',
            'password': 'newpassword123',
            'email': 'new@example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 2) # One from setUp, one new
        self.assertTrue(Customer.objects.filter(username='newuser').exists())

    def test_jwt_login(self):
        """
        Ensure a customer can log in and receive JWT tokens.
        """
        url = reverse('jwt_login')
        data = {'username': 'testuser', 'password': 'testpassword123'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_profile_view_and_update(self):
        """
        Ensure an authenticated customer can view and update their profile.
        """
        url = reverse('customer-profile')
        
        # 1. authenticate the client
        self.client.force_authenticate(user=self.customer)
        
        # 2. test get request
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.customer.username)
        
        # 3. test patch (update) request
        update_data = {'first_name': 'Test', 'last_name': 'User'}
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Test')
        
        # 4. verify the database was updated
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.first_name, 'Test')

    def test_unauthenticated_profile_access(self):
        """
        Ensure unauthenticated users cannot access the profile view.
        """
        url = reverse('customer-profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_address_crud(self):
        """
        Ensure a customer can create, list, retrieve, and delete addresses.
        """
        list_create_url = reverse('address-list') # drf router default name
        self.client.force_authenticate(user=self.customer)

        # create
        response = self.client.post(list_create_url, self.address_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Address.objects.count(), 1)
        address_id = response.data['id']

        # list
        response = self.client.get(list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # delete
        detail_url = reverse('address-detail', kwargs={'pk': address_id})
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # self.assertEqual(Address.objects.count(), 0)
        self.assertTrue(Address.objects.get(id=address_id).is_deleted)
