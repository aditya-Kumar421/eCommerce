from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from bson import ObjectId
from .redis_client import redis_client
import json

def check_admin_role(request):
    """Custom function to check if user is authenticated and has admin role"""
    user = request.user
    # Check if user is a dict and has 'role' key with value 'admin'
    if not isinstance(user, dict) or 'role' not in user or user['role'] != 'admin':
        return False
    return True

class CategoryListView(APIView):
    def get(self, request):
        categories = Category.get_all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        if not check_admin_role(request):
            return Response(
                {"error": "Only admin users can create categories"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            category_id = serializer.save()
            return Response({'id': str(category_id)}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryDetailView(APIView):
    def get(self, request, category_id):
        category = Category.get_by_id(category_id)
        if not category:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(category)
        return Response(serializer.data)
    
    def put(self, request, category_id):
        if not check_admin_role(request):
            return Response(
                {"error": "Only admin users can update categories"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        category = Category.get_by_id(category_id)
        if not category:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, category_id):
        if not check_admin_role(request):
            return Response(
                {"error": "Only admin users can delete categories"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        result = Category.delete(category_id)
        if result == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProductListView(APIView):
    def get(self, request):
        # Define cache key for all products
        cache_key = "products:all"
        cached_data = redis_client.get(cache_key)
        
        if cached_data:
            # Return cached data if available
            # print("Cache hit for products")
            return Response(json.loads(cached_data))
        
        # Fetch from MongoDB if not in cache
        # print("Cache miss for products")
        products = Product.get_all()
        serializer = ProductSerializer(products, many=True)
        data = serializer.data
        
        # Store in cache with a TTL (e.g., 1 hour = 3600 seconds)
        redis_client.setex(cache_key, 3600, json.dumps(data))
        return Response(data)
    
    def post(self, request):
        if not check_admin_role(request):
            return Response(
                {"error": "Only admin users can create products"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.save()
            # Invalidate the product list cache
            redis_client.delete("products:all")
            return Response({'id': str(product_id)}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductDetailView(APIView):
    def get(self, request, product_id):
        # Define cache key for specific product
        cache_key = f"product:{product_id}"
        cached_data = redis_client.get(cache_key)
        
        if cached_data:
            # Return cached data if available
            return Response(json.loads(cached_data))
        
        # Fetch from MongoDB if not in cache
        product = Product.get_by_id(product_id)
        if not product:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(product)
        data = serializer.data
        
        # Store in cache with a TTL (e.g., 1 hour = 3600 seconds)
        redis_client.setex(cache_key, 3600, json.dumps(data))
        return Response(data)
    
    def put(self, request, product_id):
        if not check_admin_role(request):
            return Response(
                {"error": "Only admin users can update products"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        product = Product.get_by_id(product_id)
        if not product:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            updated_product = serializer.save()
            serializer = ProductSerializer(updated_product)
            data = serializer.data
            
            # Update cache for this product and invalidate product list cache
            redis_client.setex(f"product:{product_id}", 3600, json.dumps(data))
            redis_client.delete("products:all")
            return Response(data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, product_id):
        if not check_admin_role(request):
            return Response(
                {"error": "Only admin users can delete products"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        result = Product.delete(product_id)
        if result == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        # Remove from cache and invalidate product list cache
        redis_client.delete(f"product:{product_id}")
        redis_client.delete("products:all")
        return Response(status=status.HTTP_204_NO_CONTENT)