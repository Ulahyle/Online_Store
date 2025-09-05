from rest_framework import serializers
from reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'rating', 'title', 'body', 'customer', 'created_at']
        read_only_fields = ['product'] # Product is set from the URL
