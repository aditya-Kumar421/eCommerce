from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Coupon
from .serializers import CouponSerializer
from orders.models import Order  # Import Order for applying coupons
from datetime import datetime
from bson import Decimal128

class CouponListView(APIView):

    def post(self, request):
        """Create a coupon (admin only)."""
        if request.user.get("role") != "admin":
            return Response({"error": "Only admins can create coupons"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CouponSerializer(data=request.data)
        if serializer.is_valid():
            coupon = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CouponDetailView(APIView):
    def get(self, request, coupon_id):
        """View a specific coupon."""
        coupon = Coupon.get_by_id(coupon_id)
        if not coupon:
            return Response({"error": "Coupon not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CouponSerializer(coupon)
        return Response(serializer.data)

    def put(self, request, coupon_id):
        """Update a coupon (admin only)."""
        if request.user.get("role") != "admin":
            return Response({"error": "Only admins can update coupons"}, status=status.HTTP_403_FORBIDDEN)
        
        coupon = Coupon.get_by_id(coupon_id)
        if not coupon:
            return Response({"error": "Coupon not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CouponSerializer(coupon, data=request.data, partial=True)
        if serializer.is_valid():
            updated_coupon = serializer.save()
            return Response(CouponSerializer(updated_coupon).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ApplyCouponView(APIView):
    def post(self, request):
        """Apply a coupon to the user's cart/order."""
        user_id = request.user.get("_id")
        if not user_id:
            return Response({"error": "User ID not found in token"}, status=status.HTTP_400_BAD_REQUEST)
        user_id = str(user_id)
        
        code = request.data.get("code")
        if not code:
            return Response({"error": "Coupon code is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        coupon = Coupon.get_by_code(code)
        if not coupon:
            return Response({"error": "Invalid coupon code"}, status=status.HTTP_404_NOT_FOUND)
        
        # Validate coupon
        if coupon["expiry_date"] < datetime.utcnow():
            return Response({"error": "Coupon has expired"}, status=status.HTTP_400_BAD_REQUEST)
        if coupon["used_count"] >= coupon["usage_limit"]:
            return Response({"error": "Coupon usage limit reached"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get user's cart (assuming from cart app)
        from cart.models import Cart
        cart = Cart.get_by_user_id(user_id)
        if not cart or not cart["items"]:
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
        
        total_amount = cart["total_price"]
        if coupon["min_order_value"] and total_amount < float(coupon["min_order_value"].to_decimal() if isinstance(coupon["min_order_value"], Decimal128) else coupon["min_order_value"]):
            return Response({"error": f"Order value must be at least {coupon['min_order_value']}"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate discount
        if coupon["discount_type"] == "percentage":
            discount_applied = total_amount * (coupon["discount_value"] / 100)
        else:  # amount
            discount_applied = min(total_amount, coupon["discount_value"])  # Cap at total_amount
        
        final_amount = total_amount - discount_applied
        
        # Return preview (not saving order yet)
        return Response({
            "coupon_id": coupon["_id"],
            "code": coupon["code"],
            "discount_applied": discount_applied,
            "total_amount": total_amount,
            "final_amount": final_amount
        })