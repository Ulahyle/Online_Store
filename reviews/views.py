from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from reviews.models import Review
from reviews.serializers import ReviewSerializer
from market.models import Product
from django.shortcuts import get_object_or_404


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # filter reviews based on the product_pk from the url
        product_pk = self.kwargs['product_pk']
        return Review.objects.filter(product_id=product_pk)

    def perform_create(self, serializer):
        # automatically associate the review with the product from the url and the logged-in user
        product = get_object_or_404(Product, pk=self.kwargs['product_pk'])
        serializer.save(customer=self.request.user, product=product)
