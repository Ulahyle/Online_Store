from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from accounts.models import Customer
from market.models import Product, Store, Category


class MarketTests(APITestCase):

    def setUp(self):
        # users
        self.customer = Customer.objects.create_user(username='customer', password='pass123')
        self.vendor = Customer.objects.create_user(username='vendor', password='pass123', is_vendor=True)
        
        # store for vendor
        self.store = Store.objects.create(owner=self.vendor, name="Vendor Store", slug='vendor-store')
        self.category = Category.objects.create(name='Electronics', slug='electronics')
        
        # sample product
        self.product = Product.objects.create(
            store=self.store,
            name="Sample Product",
            slug='sample-product',
            price=10.0,
            stock=100,
            category=self.category
        )

    def test_public_product_list(self):
        """Non-authenticated users can list products"""
        # correct url for the public viewset
        url = reverse('public-product-list') 
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_customer_cannot_create_product(self):
        """Regular customer cannot create a product using the dashboard endpoint"""
        self.client.force_authenticate(user=self.customer)
        # correct url for the vendor dashboard
        url = reverse('product-list') 
        data = {"name": "New Product", "slug": "new-product", "price": 5.0, "stock": 10, "category": "electronics"}
        response = self.client.post(url, data, format='json')
        # a regular customer doesn't even have a store, so they can't access this dashboard endpoint.
        # depending on exact viewset logic, this could be 403 Forbidden or an empty queryset leading to a 404. 403 is good.
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_vendor_can_create_product(self):
        """Vendor can create a product"""
        self.client.force_authenticate(user=self.vendor)
        # correct url for the vendor dashboard
        url = reverse('product-list')
        data = {"name": "Vendor Product", "slug": "vendor-product", "price": 20.0, "stock": 50, "category": "electronics"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)

    def test_vendor_sees_only_own_products_in_dashboard(self):
        """Vendor can only see products from their own store in their dashboard"""
        # create another vendor and store to ensure proper filtering
        other_vendor = Customer.objects.create_user(username='other_vendor', password='password', is_vendor=True)
        other_store = Store.objects.create(owner=other_vendor, name="Other Store", slug='other-store')
        Product.objects.create(store=other_store, name="Other Product", slug='other-product', price=5.0, stock=20, category=self.category)
        
        self.client.force_authenticate(user=self.vendor)
        # correct URLurl for the vendor dashboard
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # should only see the 1 product from their store
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Sample Product")
