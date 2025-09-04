from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from cart.models import Cart, CartItem

from cart.serializers import(
    CartSerializer,
    CartItemSerializer,
    AddCartItemSerializer,
    UpdateCartItemSerializer
)


class CartViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return AddCartItemSerializer
        if self.action == 'partial_update':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        # get_or_create method returns a tuple (object, created)
        cart, _ = Cart.objects.get_or_create(customer=self.request.user)
        return {"cart_id": cart.id}
    
    def get_queryset(self):
        # get_or_create method returns a tuple (object, created)
        cart, _ = Cart.objects.get_or_create(customer=self.request.user)
        return CartItem.objects.filter(cart=cart)

    def list(self, request, *args, **kwargs):
        # get_or_create method returns a tuple (object, created)
        cart, _ = Cart.objects.get_or_create(customer=self.request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
