from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<str:category_id>/', views.CategoryDetailView.as_view(), name='category-detail'),
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/<str:product_id>/', views.ProductDetailView.as_view(), name='product-detail'),
]