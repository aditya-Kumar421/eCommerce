from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Coupon
from orders.models import Order  # Assuming an Order model exists
from .serializers import CouponSerializer
from rest_framework.throttling import ScopedRateThrottle

class ApplyCouponView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'checkout'

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        coupon_code = request.data.get("coupon_code")
        order_total = request.data.get("order_total")

        if not coupon_code or not order_total:
            return Response({"error": "Coupon code and order total are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            coupon = Coupon.objects.get(code=coupon_code)
        except Coupon.DoesNotExist:
            return Response({"error": "Invalid coupon code"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if coupon is valid
        is_valid, message = coupon.is_valid(user, order_total)
        if not is_valid:
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

        # Apply the discount
        discounted_total = coupon.apply_discount(order_total)

        return Response({
            "message": "Coupon applied successfully!",
            "original_total": order_total,
            "discounted_total": discounted_total,
            "discount_value": order_total - discounted_total
        }, status=status.HTTP_200_OK)


class CreateCouponView(APIView): # Only admins can create coupons
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'checkout'
    
    permission_classes = [IsAuthenticated]
    def post(self, request):
        if request.user.role != 'admin':
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CouponSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Coupon created successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)