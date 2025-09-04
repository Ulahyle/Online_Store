from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from accounts.models import Customer, Address
from market.models import Product, Store, Category
from cart.models import Cart, CartItem
from order.models import Order


class OrderTests(APITestCase):

    def setUp(self):
        self.user = Customer.objects.create_user(username='user', password='pass123')
        vendor = Customer.objects.create_user(username='vendor', password='password', is_vendor=True)
        store = Store.objects.create(owner=vendor, name="Test Store", slug='test-store')
        category = Category.objects.create(name='Tests', slug='tests')
        self.product = Product.objects.create(
            name="Test Product", price=10.00, stock=10, store=store, category=category, slug='test-prod'
        )
        self.address = Address.objects.create(
            customer=self.user, country="coun00", province="00", city="city00", postal_code="00000000"
        )
        self.client.force_authenticate(user=self.user)

    def test_create_order_success(self):
        # add item to the user's cart first
        cart, _ = Cart.objects.get_or_create(customer=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)

        url = reverse('order-list')
        # we must provide the required shipping_address_id
        data = {"shipping_address_id": self.address.id}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # verify Product stock was reduced
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 8)
        
        # verify Cart is now empty
        self.assertFalse(CartItem.objects.filter(cart__customer=self.user).exists())
        
        # verify Order was created
        self.assertTrue(Order.objects.filter(customer=self.user, grand_total=20.00).exists())

    def test_create_order_empty_cart(self):
        url = reverse('order-list')
        data = {"shipping_address_id": self.address.id}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_order_history(self):
        # create an order first before trying to list it
        cart, _ = Cart.objects.get_or_create(customer=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=1)
        self.client.post(reverse('order-list'), {"shipping_address_id": self.address.id}, format='json')

        url = reverse('order-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
