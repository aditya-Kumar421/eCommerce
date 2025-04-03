from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from .serializers import OrderSerializer
from .tasks import send_order_status_email

class OrderView(APIView):
    def get(self, request):
        """View all orders for the user."""
        user_id = request.user.get("_id")
        if not user_id:
            return Response({"error": "User ID not found in token"}, status=status.HTTP_400_BAD_REQUEST)
        user_id = str(user_id)
        
        orders = Order.get_by_user_id(user_id)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Create an order from the cart."""
        user_id = request.user.get("_id")
        if not user_id:
            return Response({"error": "User ID not found in token"}, status=status.HTTP_400_BAD_REQUEST)
        user_id = str(user_id)
        
        # Check user role (assuming 'role' in request.user)
        if request.user.get("role") != "customer" and request.user.get("role") != "admin":
            return Response({"error": "Only customers can place orders"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = OrderSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            order = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderDetailView(APIView):
    def get(self, request, order_id):
        """View a specific order."""
        user_id = request.user.get("_id")
        if not user_id:
            return Response({"error": "User ID not found in token"}, status=status.HTTP_400_BAD_REQUEST)
        user_id = str(user_id)
        
        order = Order.get_by_id(order_id)
        if not order or order["user_id"] != user_id and request.user.get("role") != "admin":
            return Response({"error": "Order not found or access denied"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def put(self, request, order_id):
        """Update order status (admin only)."""
        user_id = request.user.get("_id")
        if not user_id:
            return Response({"error": "User ID not found in token"}, status=status.HTTP_400_BAD_REQUEST)
        
        if request.user.get("role") != "admin":
            return Response({"error": "Only admins can update order status"}, status=status.HTTP_403_FORBIDDEN)
        
        order = Order.get_by_id(order_id)
        if not order:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Pass request context to serializer
        serializer = OrderSerializer(order, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            updated_order = serializer.save()
            if request.data.get("status") != order["status"]:  # Check if status changed
                user_email = request.user.get("email")  # Adjust to fetch customer email if needed
                send_order_status_email.delay(order_id, user_email)
            return Response(OrderSerializer(updated_order).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)