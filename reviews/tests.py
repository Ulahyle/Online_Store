from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from accounts.models import Customer
from market.models import Product, Store, Category


class ReviewTests(APITestCase):
    def setUp(self):
        self.user = Customer.objects.create_user(username='user', password='pass123')
        vendor = Customer.objects.create_user(username='vendor', password='password', is_vendor=True)
        store = Store.objects.create(owner=vendor, name="Test Store", slug='test-store')
        category = Category.objects.create(name='Tests', slug='tests')
        self.product = Product.objects.create(
            name="Test Product", price=10, stock=50, store=store, category=category, slug='test-prod'
        )
        self.review_data = {
            "rating": 5,
            "title": "Amazing Product!",
            "body": "I really loved this, would buy again."
        }

    def test_unauthenticated_user_can_list_reviews(self):
        """Anyone can see the reviews for a product."""
        url = reverse('product-reviews-list', kwargs={'product_pk': self.product.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cannot_create_review(self):
        """A user must be logged in to post a review."""
        url = reverse('product-reviews-list', kwargs={'product_pk': self.product.pk})
        response = self.client.post(url, self.review_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_authenticated_user_can_create_review(self):
        """A logged-in user can successfully post a review."""
        self.client.force_authenticate(user=self.user)
        url = reverse('product-reviews-list', kwargs={'product_pk': self.product.pk})
        response = self.client.post(url, self.review_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(response.data['customer'], self.user.username)
