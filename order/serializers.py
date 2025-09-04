from rest_framework import serializers
from order.models import Order, OrderItem
from accounts.models import Address
from market.models import Product


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField()
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'unit_price_snapshot']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = serializers.StringRelatedField()
    
    class Meta:
        model = Order
        fields = ['id', 'customer', 'order_number', 'status', 'grand_total', 'placed_at', 'shipping_address', 'items']

class CreateOrderSerializer(serializers.Serializer):
    shipping_address_id = serializers.IntegerField()

    def validate_shipping_address_id(self, value):
        user = self.context['request'].user
        if not Address.objects.filter(pk=value, customer=user).exists():
            raise serializers.ValidationError("Invalid address ID provided.")
        return value

class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']
