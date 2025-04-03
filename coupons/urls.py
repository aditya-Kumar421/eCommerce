from django.urls import path
from .views import CouponListView, CouponDetailView, ApplyCouponView

urlpatterns = [
    path('create/', CouponListView.as_view(), name='coupon-list'),
    path('update/<str:coupon_id>/', CouponDetailView.as_view(), name='coupon-detail'),
    path('apply/', ApplyCouponView.as_view(), name='apply-coupon'),
]