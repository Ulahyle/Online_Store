from rest_framework import serializers
from market.models import Store, Category, Product, ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'alt_text', 'display_order']

class CategorySerializer(serializers.ModelSerializer):
    # this field will contain the path from the leaf to the root
    path = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent', 'path']

    def get_path(self, obj):
        path = [obj.name]
        current = obj
        while current.parent:
            current = current.parent
            path.insert(0, current.name)
        return path

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    # use SlugRelatedField for a more readable representation of the category
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.filter(is_active=True)
    )

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'discount_price',
            'stock', 'is_active', 'store', 'category', 'images'
        ]
        # store will be set automatically based on the logged-in vendor
        read_only_fields = ['store']

class StoreSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Store
        fields = ['id', 'name', 'slug', 'description', 'is_active', 'products']
