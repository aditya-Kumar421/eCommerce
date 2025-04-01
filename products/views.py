from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from .models import Product, Category
from .serializer import ProductSerializer, CategorySerializer
from .permissions import IsAdminUser
from django.core.cache import cache
from rest_framework.throttling import ScopedRateThrottle
from django.http import HttpResponse
from upstash_redis import Redis
import json

class CategoryListView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'products'

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if not request.user.is_authenticated or request.user.role != 'admin':
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Initialize Redis (use environment variables for security)
redis = Redis(
    url="https://quality-hamster-50979.upstash.io",
    token="AccjAAIjcDE4YzhiOWY5NGU0ZWI0MzkxOTkxNGJiMzM3YTZhZmVmNnAxMA"
)

class ProductListCreateView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "products"

    def get(self, request):
        cache_key = "all_products"
        cached_products = redis.get(cache_key)  # Try fetching from Redis

        if not cached_products:
            products = Product.objects.all()
            serializer = ProductSerializer(products, many=True)
            redis.set(cache_key,  json.dumps(serializer.data), ex=60 * 15)
            products = serializer.data  # Cache for 15 minutes
        else:
            print("Fetching product from Redis cache...")
            products = json.loads(cached_products)

        return Response(products, status=status.HTTP_200_OK)

    def post(self, request):
        if not request.user.is_authenticated or request.user.role != "admin":
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            redis.delete("all_products")  # Invalidate cache when a new product is added
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "products"

    def get(self, request, pk):
        cache_key = f"product_{pk}"
        cached_product = redis.get(cache_key)  # Try fetching from Redis

        if cached_product:
            print("Fetching product from Redis cache...")
            product = json.loads(cached_product)  # Convert JSON string back to dictionary
        else:
            print("Fetching product from Database...")
            product_obj = get_object_or_404(Product, pk=pk)
            serializer = ProductSerializer(product_obj)
            product = serializer.data  # Use serialized product data
            redis.set(cache_key, json.dumps(product), ex=60 * 15)  # Store JSON string in Redis

        return Response(product, status=status.HTTP_200_OK)

    def put(self, request, pk):
        if not request.user.is_authenticated or request.user.role != "admin":
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            redis.delete(f"product_{pk}")  # Invalidate product cache on update
            redis.delete("all_products")  # Invalidate product list cache
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not request.user.is_authenticated or request.user.role != "admin":
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        product = get_object_or_404(Product, pk=pk)
        product.delete()
        redis.delete(f"product_{pk}")  # Invalidate product cache on delete
        redis.delete("all_products")  # Invalidate product list cache
        return Response({"message": "Product deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

'''Without Cache'''

# class ProductListCreateView(APIView):
#     throttle_classes = [ScopedRateThrottle]
#     throttle_scope = 'products'

#     def get(self, request):
#         products = Product.objects.all()
#         serializer = ProductSerializer(products, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def post(self, request):
#         if not request.user.is_authenticated or request.user.role != 'admin':
#             return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

#         serializer = ProductSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class ProductDetailView(APIView):
#     throttle_classes = [ScopedRateThrottle]
#     throttle_scope = 'products'

#     def get(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         serializer = ProductSerializer(product)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def put(self, request, pk):
#         if not request.user.is_authenticated or request.user.role != 'admin':
#             return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

#         product = get_object_or_404(Product, pk=pk)
#         serializer = ProductSerializer(product, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk):
#         if not request.user.is_authenticated or request.user.role != 'admin':
#             return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

#         product = get_object_or_404(Product, pk=pk)
#         product.delete()
#         return Response({"message": "Product deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
