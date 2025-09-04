from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from accounts.models import Customer
from market.models import Product, Store, Category
from cart.models import Cart, CartItem


class CartTests(APITestCase):

    def setUp(self):
        self.user = Customer.objects.create_user(username='user', password='pass123')
        # create dependencies for the product
        vendor = Customer.objects.create_user(username='vendor', password='password', is_vendor=True)
        store = Store.objects.create(owner=vendor, name="Test Store", slug='test-store')
        category = Category.objects.create(name='Tests', slug='tests')
        self.product = Product.objects.create(
            name="Test Product", 
            price=10.00, 
            stock=50, 
            store=store, 
            category=category,
            slug='test-product'
        )
        self.client.force_authenticate(user=self.user)

    def test_unauthenticated_cart_access(self):
        # log out the client for this test
        self.client.logout()
        url = reverse('cart-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_item_to_cart(self):
        url = reverse('cart-list') # post to the list endpoint to create an item
        data = {"product_id": self.product.id, "quantity": 2}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # verify the cart item was created with the correct quantity
        self.assertTrue(CartItem.objects.filter(cart__customer=self.user, product=self.product, quantity=2).exists())

    def test_update_cart_item_quantity(self):
        # first, add an item to the cart
        cart, _ = Cart.objects.get_or_create(customer=self.user)
        cart_item = CartItem.objects.create(cart=cart, product=self.product, quantity=1)
        
        url = reverse('cart-detail', kwargs={'pk': cart_item.id}) # use 'cart-detail' for specific items
        data = {"quantity": 3}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 3)

    def test_remove_cart_item(self):
        cart, _ = Cart.objects.get_or_create(customer=self.user)
        cart_item = CartItem.objects.create(cart=cart, product=self.product, quantity=1)
        
        url = reverse('cart-detail', kwargs={'pk': cart_item.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CartItem.objects.filter(id=cart_item.id).exists())
