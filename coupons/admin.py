from django.contrib import admin
from .models import Coupon
# Register your models here.

@admin.register(Coupon)
class Coupon(admin.ModelAdmin):
    list_display = ('id', 'code', 'discount_value', 'expiry_date')
