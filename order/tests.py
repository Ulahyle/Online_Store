from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from unittest.mock import patch
from django.contrib.auth import get_user_model
from accounts.models import Address
from market.models import Product, Store, Category
from cart.models import Cart, CartItem
from order.models import Order, OrderItem
from order.tasks import send_order_confirmation_email


User = get_user_model()

class OrderTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='user', password='pass123')
        vendor = User.objects.create_user(username='vendor', password='password', is_vendor=True)
        store = Store.objects.create(owner=vendor, name="Test Store", slug='test-store')
        category = Category.objects.create(name='Tests', slug='tests')
        self.product = Product.objects.create(
            name="Test Product", price=10.00, stock=10, store=store, category=category, slug='test-prod'
        )
        self.address = Address.objects.create(
            customer=self.user,
            country="coun00",
            province="00",
            city="city00",
            postal_code="00000000"
        )
        self.client.force_authenticate(user=self.user)

    def test_create_order_success(self):
        # add item to the user's cart first
        cart, _ = Cart.objects.get_or_create(customer=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)

        url = reverse('order-list')
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

class TaskTests(APITestCase):
    def setUp(self):
        # create a user
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )
        # create a vendor and store
        self.vendor = User.objects.create_user(username='vendor_task', password='password', is_vendor=True)
        self.store = Store.objects.create(owner=self.vendor, name="Test Store", slug='test-store-task')
        # create a category
        self.category = Category.objects.create(name='Tests', slug='tests')

        # create a product
        self.product = Product.objects.create(
            name='Test Product',
            description='A test product.',
            price=10.00,
            stock=100,
            store=self.store,
            category=self.category,
            slug='test-prod-task'
        )

        # create an address for this user (fixes the previous ValueError)
        self.address = Address.objects.create(
            customer=self.user,
            country="coun11",
            province="11",
            city="city11",
            postal_code="11111111"
        )

        # create an order with a real address FK
        self.order = Order.objects.create(
            customer=self.user,
            shipping_address=self.address,
            order_number='test-order-123',
            grand_total=10.00
        )

        # create an order item for the order
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            unit_price_snapshot=self.product.price
        )

    @patch('order.tasks.send_mail')
    def test_send_order_confirmation_email_success(self, mock_send_mail):
        """
        Test that the order confirmation email task sends a valid email.
        """
        send_order_confirmation_email(self.order.id)

        self.assertTrue(mock_send_mail.called)
        mock_send_mail.assert_called_with(
            f'Order Confirmation: {self.order.order_number}',
            f'Hi ,\n\nYour order has been placed successfully. Your order number is {self.order.order_number}.',
            'no-reply@onlinestore.com',
            [self.user.email],
)
        