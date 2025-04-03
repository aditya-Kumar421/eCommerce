from rest_framework import serializers
from .models import Category, Product
from bson import ObjectId, Decimal128
from rest_framework import serializers
from .models import Category, Product

class CategorySerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True, source='_id')
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=1000, required=False)
    
    def create(self, validated_data):
        return Category.create(validated_data)
    
    def update(self, instance, validated_data):
        Category.update(str(instance['_id']), validated_data)
        # Fetch the updated document
        updated_instance = Category.get_by_id(str(instance['_id']))
        return updated_instance


class ProductSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True, source='_id')
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=1000)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    availability = serializers.BooleanField(default=True)
    category_id = serializers.CharField(max_length=24)
    image = serializers.ImageField(write_only=True, required=False)
    image_url = serializers.CharField(read_only=True)
    
    def validate_availability(self, value):
        print(f"Validating availability: {value} (type: {type(value)})")
        if value is None:
            return True
        if isinstance(value, str):
            value = value.strip().lower()
            if not value:
                return True
            if value in ('true', '1', 'yes', 'on'):
                return True
            if value in ('false', '0', 'no', 'off'):
                return False
            raise serializers.ValidationError("Must be a valid boolean.")
        elif isinstance(value, (bool, int)):
            return bool(value)
        raise serializers.ValidationError("Must be a valid boolean.")

    def validate_category_id(self, value):
        try:
            if not Category.get_by_id(value):
                raise serializers.ValidationError("Category does not exist")
            return value
        except:
            raise serializers.ValidationError("Invalid category_id format")
    
    def create(self, validated_data):
        # Convert Decimal to Decimal128 for MongoDB
        if 'price' in validated_data:
            validated_data['price'] = Decimal128(validated_data['price'])
        image_file = validated_data.pop('image', None)
        return Product.create(validated_data, image_file)
    
    def update(self, instance, validated_data):
        if 'price' in validated_data:
            validated_data['price'] = Decimal128(validated_data['price'])
        image_file = validated_data.pop('image', None)
        # Ensure Product.update returns the updated document
        Product.update(str(instance['_id']), validated_data, image_file)
        # Fetch the updated document
        return Product.get_by_id(str(instance['_id']))