from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Order, OrderItem
from .serializers import OrderSerializer
from cart.models import Cart
from coupons.models import Coupon 
from decimal import Decimal
from django.db import transaction
from cart.serializers import CartSerializer
from rest_framework.throttling import ScopedRateThrottle

class PlaceOrderView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'order'

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        coupon_code = request.data.get("coupon_code", None)

        # Fetch user's cart
        try:
            cart = Cart.objects.get(user=user)  # Assuming each user has one cart
        except Cart.DoesNotExist:
            return Response({"error": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        if not cart.items.exists():
            return Response({"error": "Your cart has no items."}, status=status.HTTP_400_BAD_REQUEST)
        # print(cart)

        cart_serializer = CartSerializer(cart)
        total_amount = Decimal(str(cart_serializer.data["total_price"]))  # Ensure consistency with Decimal type

        discount_applied = Decimal(0)
        coupon = None

        # Apply coupon if provided
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                if coupon.is_valid(user, total_amount):
                    discount_applied = coupon.apply_discount(total_amount)
                    coupon.used_count += 1
                    coupon.save()
                else:
                    return Response({"error": "Invalid or expired coupon."}, status=status.HTTP_400_BAD_REQUEST)
            except Coupon.DoesNotExist:
                return Response({"error": "Invalid coupon code."}, status=status.HTTP_400_BAD_REQUEST)

        final_amount = total_amount - discount_applied

        with transaction.atomic():  # Ensures rollback if anything fails
            # Create order
            order = Order.objects.create(
                user=user,
                total_amount=total_amount,
                discount_applied=discount_applied,
                final_amount=final_amount,
                status="Pending"
            )

            # Move cart items to order and clear the cart
        cart_items = cart.items.all()
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity
            )

        # Clear cart after order placement
        cart_items.delete()  # Remove all cart items first
        cart.total_price = 0  
        cart.total_items = 0
        cart.save()

        serializer = OrderSerializer(order)

        return Response({
            "message": "Order placed successfully! Cart is now empty.",
            "order": serializer.data
        }, status=status.HTTP_201_CREATED)



class OrderListView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'order'
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateOrderStatusView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'order'

    permission_classes = [IsAuthenticated] 

    def patch(self, request, order_id):

        if request.user.role != 'admin':
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get("status")
        if new_status not in ['Pending', 'Shipped', 'Delivered']:
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        order.status = new_status
        order.save()
        return Response({"message": "Order status updated!"}, status=status.HTTP_200_OK)
