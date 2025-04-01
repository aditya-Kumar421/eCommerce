from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('user.urls')),
    path('api/', include('products.urls')),
    path('cart/', include('cart.urls')),
    path('order/', include('orders.urls')),
    path('coupon/', include('coupons.urls')),
]
