from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from order.models import Order, OrderItem
from cart.models import Cart, CartItem
from order.serializers import OrderSerializer, CreateOrderSerializer, UpdateOrderSerializer
from core.permissions import IsVendor
from order.tasks import send_order_confirmation_email
from django.db.models import Sum, F
import uuid


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_vendor:
            # vendor sees orders containing their products
            return Order.objects.filter(items__product__store__owner=user).distinct()
        # customer sees their own orders
        return Order.objects.filter(customer=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateOrderSerializer
        if self.action in ['update', 'partial_update'] and self.request.user.is_vendor:
            return UpdateOrderSerializer
        return OrderSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        cart = Cart.objects.filter(customer=request.user).first()
        if not cart or cart.items.count() == 0:
            return Response({"detail": "Ur cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            cart_items = cart.items.all()
            grand_total = cart_items.aggregate(total=Sum(F('product__price') * F('quantity')))['total'] or 0

            # create the order
            order = Order.objects.create(
                customer=request.user,
                shipping_address_id=serializer.validated_data['shipping_address_id'],
                order_number=str(uuid.uuid4()),
                grand_total=grand_total
            )
            
            # create order items from cart items
            for item in cart.items.all():
                if item.product.stock < item.quantity:
                    return Response({"detail": f"Not enough stock for {item.product.name}."}, status=status.HTTP_400_BAD_REQUEST)
                
                order_item = OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    unit_price_snapshot=item.product.price # price snapshot
                )
                
                # decrease product stock
                item.product.stock -= item.quantity
                item.product.save()

            # update order total and clear cart
            cart.items.all().delete()
            
            send_order_confirmation_email.delay(order.id)

            response_serializer = OrderSerializer(order)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
