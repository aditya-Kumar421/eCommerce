from rest_framework import serializers
from .models import Order, OrderItem
from cart.models import Cart, CartItem
from coupons.models import Coupon
from decimal import Decimal
class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'total_amount', 'discount_applied', 'final_amount', 'status', 'created_at']
        read_only_fields = ['id', 'user', 'discount_applied', 'final_amount', 'status', 'created_at']

# class OrderSerializer(serializers.ModelSerializer):
#     coupon_code = serializers.CharField(write_only=True, required=False, allow_null=True)
#     user = serializers.HiddenField(default=serializers.CurrentUserDefault()) 

#     class Meta:
#         model = Order
#         fields = ['id', 'user', 'total_amount', 'discount_applied', 'final_amount', 'coupon_code', 'status', 'created_at']
#         read_only_fields = ['discount_applied', 'final_amount', 'status', 'created_at']

        
#     def create(self, validated_data):
#         """Handle coupon validation and apply discount"""
#         request = self.context.get('request')  
#         if not request:
#             raise serializers.ValidationError({"error": "Request context missing."})
        
#         user = request.user
#         coupon_code = validated_data.pop('coupon_code', None)
#         total_amount = validated_data.get('total_amount')

#         discount_applied = 0.0
#         coupon = None

#         if coupon_code:
#             try:
#                 coupon = Coupon.objects.get(code=coupon_code)

#                 if coupon.is_valid(user, total_amount):  
#                     discount_applied = coupon.apply_discount(total_amount)
#                     coupon.used_count += 1
#                     coupon.save()
#                 else:
#                     raise serializers.ValidationError({"error": "Invalid or expired coupon"})
#             except Coupon.DoesNotExist:
#                 raise serializers.ValidationError({"error": "Invalid coupon code"})

#         validated_data['user'] = user  
#         validated_data['discount_applied'] = discount_applied
#         validated_data['final_amount'] = Decimal(total_amount) - Decimal(discount_applied)
#         validated_data['coupon'] = coupon

#         return super().create(validated_data)

