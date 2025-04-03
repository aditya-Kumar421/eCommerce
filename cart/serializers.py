from rest_framework import serializers
from .models import Cart

class CartItemSerializer(serializers.Serializer):
    product_id = serializers.CharField(max_length=24)
    name = serializers.CharField(max_length=200)
    price = serializers.FloatField()
    quantity = serializers.IntegerField(min_value=1)

class CartSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    items = CartItemSerializer(many=True)
    total_items = serializers.IntegerField()
    total_price = serializers.FloatField()

    def create(self, validated_data):
        user_id = validated_data["user_id"]
        items = validated_data.get("items", [])
        total_items = sum(item["quantity"] for item in items)
        total_price = sum(item["price"] * item["quantity"] for item in items)
        return Cart.update(user_id, {
            "user_id": user_id,
            "items": items,
            "total_items": total_items,
            "total_price": total_price
        })

    def update(self, instance, validated_data):
        user_id = instance["user_id"]
        items = validated_data.get("items", instance["items"])
        total_items = sum(item["quantity"] for item in items)
        total_price = sum(item["price"] * item["quantity"] for item in items)
        return Cart.update(user_id, {
            "items": items,
            "total_items": total_items,
            "total_price": total_price
        })