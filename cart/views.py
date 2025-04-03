from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cart
from .serializers import CartSerializer, CartItemSerializer

class CartView(APIView):
    def get(self, request):
        """View all items in the user's cart."""
        print("request.user:", request.user)  # Debug
        user_id = request.user.get("_id")  # Use "_id" key
        print("Extracted user_id before str:", user_id)  # Debug
        if user_id is None or user_id == "":
            return Response({"error": "User ID not found in token"}, status=status.HTTP_400_BAD_REQUEST)
        user_id = str(user_id)
        print("Final user_id:", user_id)  # Debug
        
        cart = Cart.get_by_user_id(user_id)
        if not cart:
            cart = Cart.create(user_id)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request):
        """Add an item to the cart."""
        print("request.user:", request.user)  # Debug
        user_id = request.user.get("_id")  # Use "_id" key
        print("Extracted user_id before str:", user_id)  # Debug
        if user_id is None or user_id == "":
            return Response({"error": "User ID not found in token"}, status=status.HTTP_400_BAD_REQUEST)
        user_id = str(user_id)
        print("Final user_id:", user_id)  # Debug
        
        item_serializer = CartItemSerializer(data=request.data)
        if item_serializer.is_valid():
            cart = Cart.add_item(user_id, item_serializer.validated_data)
            serializer = CartSerializer(cart)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CartItemView(APIView):
    def delete(self, request, product_id):
        """Remove an item from the cart."""
        print("request.user:", request.user)  # Debug
        user_id = request.user.get("_id")  # Use "_id" key
        print("Extracted user_id before str:", user_id)  # Debug
        if user_id is None or user_id == "":
            return Response({"error": "User ID not found in token"}, status=status.HTTP_400_BAD_REQUEST)
        user_id = str(user_id)
        print("Final user_id:", user_id)  # Debug
        
        cart = Cart.remove_item(user_id, product_id)
        if not cart:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)