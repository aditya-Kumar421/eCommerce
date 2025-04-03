from django.urls import path
from .views import CartView, CartItemView

urlpatterns = [
    path('add/', CartView.as_view(), name='cart'),
    path('remove/<str:product_id>/', CartItemView.as_view(), name='cart-item'),
]