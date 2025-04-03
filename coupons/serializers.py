from rest_framework import serializers
from .models import Coupon
from django.utils import timezone
from bson import Decimal128
from decimal import Decimal

class CouponSerializer(serializers.Serializer):
    id = serializers.CharField(source="_id", read_only=True)
    code = serializers.CharField(max_length=50)
    discount_type = serializers.ChoiceField(choices=["percentage", "amount"])
    discount_value = serializers.FloatField(min_value=0)
    expiry_date = serializers.DateTimeField()
    usage_limit = serializers.IntegerField(min_value=1)
    used_count = serializers.IntegerField(read_only=True)
    min_order_value = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)

    def validate_code(self, value):
        if Coupon.get_by_code(value) and self.instance is None:
            raise serializers.ValidationError("Coupon code already exists")
        return value

    def validate_expiry_date(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Expiry date must be in the future")
        return value

    def validate(self, data):
        if data["discount_type"] == "percentage" and data["discount_value"] > 100:
            raise serializers.ValidationError("Percentage discount cannot exceed 100")
        return data

    def create(self, validated_data):
        return Coupon.create(validated_data)

    def update(self, instance, validated_data):
        return Coupon.update(instance["_id"], validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if "min_order_value" in data and isinstance(instance.get("min_order_value"), Decimal128):
            data["min_order_value"] = float(instance["min_order_value"].to_decimal())  # Convert to float for simplicity
        return data