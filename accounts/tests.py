from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from accounts.models import Customer, Address
from unittest.mock import patch, MagicMock


class AccountTests(APITestCase):
    def setUp(self):
        self.customer = Customer.objects.create_user(
            username='testuser',
            password='testpassword123',
            email='test@example.com',
            phone_number="1234567890"
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
        url = reverse('register')
        data = {
            'username': 'newuser',
            'password': 'newpassword123',
            'email': 'new@example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 2)
        self.assertTrue(Customer.objects.filter(username='newuser').exists())

    def test_jwt_login(self):
        url = reverse('jwt_login')
        data = {'username': 'testuser', 'password': 'testpassword123'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_profile_view_and_update(self):
        url = reverse('customer-profile')
        self.client.force_authenticate(user=self.customer)

        # get profile
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.customer.username)

        # patch profile
        update_data = {'first_name': 'Test', 'last_name': 'User'}
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Test')

        self.customer.refresh_from_db()
        self.assertEqual(self.customer.first_name, 'Test')

    def test_unauthenticated_profile_access(self):
        url = reverse('customer-profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_address_crud(self):
        list_create_url = reverse('address-list')
        self.client.force_authenticate(user=self.customer)

        # create
        response = self.client.post(list_create_url, self.address_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        address_id = response.data['id']

        # list
        response = self.client.get(list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # delete (soft delete → is_deleted=True)
        detail_url = reverse('address-detail', kwargs={'pk': address_id})
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(Address.objects.get(id=address_id).is_deleted)

class OTPTests(APITestCase):
    def setUp(self):
        self.user = Customer.objects.create_user(
            username='otpuser',
            password='testpassword',
            email='otp@example.com',
            phone_number='1112223333'
        )

    @patch("accounts.views.get_redis_connection")
    def test_send_otp_success(self, mock_redis):
        mock_conn = MagicMock()
        mock_redis.return_value = mock_conn

        url = reverse('otp')
        data = {"email": "otp@example.com"}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 200)
        mock_conn.setex.assert_called()

    @patch("accounts.views.get_redis_connection")
    def test_verify_otp_success(self, mock_redis):
        mock_conn = MagicMock()
        mock_conn.get.return_value = b"123456"
        mock_redis.return_value = mock_conn

        url = reverse('verify_otp')
        data = {"email": "otp@example.com", "otp": "123456"}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    @patch("accounts.views.get_redis_connection")
    def test_otp_login_request(self, mock_redis):
        mock_conn = MagicMock()
        mock_redis.return_value = mock_conn

        url = reverse('login')
        data = {"phone_number": "1112223333"}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 200)
        mock_conn.setex.assert_called()
