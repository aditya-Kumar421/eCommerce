from django.urls import path
from .views import OrderView, OrderDetailView

urlpatterns = [
    path('place/', OrderView.as_view(), name='orders'),
    path('status/<str:order_id>/', OrderDetailView.as_view(), name='order-detail'),
]