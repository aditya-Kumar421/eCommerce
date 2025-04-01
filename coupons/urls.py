from django.urls import path
from .views import ApplyCouponView, CreateCouponView

urlpatterns = [
    path('apply/', ApplyCouponView.as_view(), name='apply-coupon'),
    path('create/', CreateCouponView.as_view(), name='create-coupon'),
]
