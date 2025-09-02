from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from core.permissions import IsVendor
from market.models import Store, Category, Product
from market.serializers import StoreSerializer, CategorySerializer, ProductSerializer
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count # using Count for best seller for simplicity


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

# public facing ViewSets (Read-only)
class PublicCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class PublicProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    # Custom action to get best-selling products
    @action(detail=False, methods=['get'])
    def best_sellers(self, request):
        # a simple way to determine best sellers is by the number of orders
        # this requires the OrderItem model to be in place
        # for now, we ll order by a simple metric, let s say by creation date as a placeholder
        # we will update this logic once OrderItem is integrated
        products = self.get_queryset().annotate(
            order_count=Count('orderitem')
        ).order_by('-order_count')[:10] # top10
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    # custom action to get best-priced products
    @action(detail=False, methods=['get'])
    def best_price(self, request):
        # sort by price, handling discount price if it exists
        products = self.get_queryset().order_by('price')[:10] # top10 cheapest
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
