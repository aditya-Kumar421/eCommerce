from rest_framework import serializers
from .models import Order
from cart.serializers import CartItemSerializer
from cart.models import Cart
from coupons.models import Coupon
from datetime import datetime
from bson import Decimal128


class OrderSerializer(serializers.Serializer):
    id = serializers.CharField(source="_id", read_only=True)
    user_id = serializers.CharField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.FloatField(read_only=True)
    discount_applied = serializers.FloatField(read_only=True)  # Make read-only
    final_amount = serializers.FloatField(read_only=True)
    coupon_id = serializers.CharField(allow_null=True, required=False)
    status = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True)

    def validate_status(self, value):
        valid_statuses = ["pending", "shipped", "delivered"]
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Status must be one of {valid_statuses}")
        return value

    def validate_coupon_id(self, value):
        if value:
            coupon = Coupon.get_by_id(value)
            if not coupon:
                raise serializers.ValidationError("Invalid coupon ID")
            if coupon["expiry_date"] < datetime.utcnow():
                raise serializers.ValidationError("Coupon has expired")
            if coupon["used_count"] >= coupon["usage_limit"]:
                raise serializers.ValidationError("Coupon usage limit reached")
        return value

    def validate(self, data):
        user_id = self.context["request"].user.get("_id")
        cart = Cart.get_by_user_id(user_id)
        if not cart or not cart["items"]:
            raise serializers.ValidationError("Cart is empty")
        
        total_amount = cart["total_price"]
        coupon_id = data.get("coupon_id")
        discount_applied = 0.0  # Default
        
        if coupon_id:
            coupon = Coupon.get_by_id(coupon_id)
            min_order_value = (float(coupon["min_order_value"].to_decimal()) if isinstance(coupon["min_order_value"], Decimal128) 
                              else coupon["min_order_value"]) if coupon["min_order_value"] is not None else None
            if min_order_value and total_amount < min_order_value:
                raise serializers.ValidationError(f"Order value must be at least {min_order_value}")
            
            # Calculate discount based on coupon type
            if coupon["discount_type"] == "percentage":
                discount_applied = total_amount * (coupon["discount_value"] / 100)
            else:  # amount
                discount_applied = min(total_amount, coupon["discount_value"])
        
        # Update validated_data with calculated values
        data["discount_applied"] = discount_applied
        data["total_amount"] = total_amount
        data["final_amount"] = total_amount - discount_applied
        return data

    def create(self, validated_data):
        user_id = self.context["request"].user.get("_id")
        cart = Cart.get_by_user_id(user_id)
        coupon_id = validated_data.get("coupon_id")
        discount_applied = validated_data.get("discount_applied", 0.0)
        return Order.create(user_id, cart, coupon_id, discount_applied)

    def update(self, instance, validated_data):
        status = validated_data.get("status", instance["status"])
        return Order.update_status(instance["_id"], status)