from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsVendor
from .models import Store, Category, Product
from .serializers import StoreSerializer, CategorySerializer, ProductSerializer
from django.shortcuts import get_object_or_404


# seller dashboard ViewSets (require IsVendor permission)
class StoreViewSet(viewsets.ModelViewSet):
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated, IsVendor]

    def get_queryset(self):
        # a vendor can only manage their own store
        return Store.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        # assign the current user as the store owner
        serializer.save(owner=self.request.user)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsVendor]
    # in a real app, you might restrict which vendors can manage which categories
    # for now, we ll allow any vendor to manage any category

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsVendor]

    def get_queryset(self):
        # a vendor can only see and manage products from their own store
        user = self.request.user
        try:
            # assuming a vendor has one store. If they can have multiple, this needs adjustment
            store = Store.objects.get(owner=user) 
            return Product.objects.filter(store=store)
        except Store.DoesNotExist:
            return Product.objects.none() # return an empty queryset if no store is found

    def perform_create(self, serializer):
        # automatically assign the product to the vendor s store
        user = self.request.user
        store = get_object_or_404(Store, owner=user)
        serializer.save(store=store)
