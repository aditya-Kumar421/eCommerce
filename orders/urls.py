from django.urls import path
from .views import PlaceOrderView, OrderListView, UpdateOrderStatusView

urlpatterns = [
    path('place/', PlaceOrderView.as_view(), name='place_order'),
    path('list/', OrderListView.as_view(), name='order_list'),
    path('update/<int:order_id>/', UpdateOrderStatusView.as_view(), name='update_order_status'),
]
