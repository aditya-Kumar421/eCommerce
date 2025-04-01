from django.db import models
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from decimal import Decimal

User = get_user_model()

class Coupon(models.Model):
    CODE_TYPE_CHOICES = [
        ('fixed', 'Fixed Amount'),
        ('percent', 'Percentage'),
    ]

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=CODE_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    expiry_date = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0)
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    applicable_users = models.ManyToManyField(User, blank=True, help_text="Users who can use this coupon")

    def is_valid(self, user, order_total):
        """Check if coupon is still valid."""
        if self.expiry_date < now():
            return False, "Coupon has expired"
        if self.used_count >= self.usage_limit:
            return False, "Coupon usage limit reached"
        if self.min_order_value and order_total < self.min_order_value:
            return False, f"Minimum order value should be {self.min_order_value}"
        if self.applicable_users.exists() and user not in self.applicable_users.all():
            return False, "You are not eligible for this coupon"
        return True, "Valid coupon"

    def apply_discount(self, order_total):
        if not isinstance(order_total, (int, float, Decimal)):  
            raise ValueError("order_total must be a number")  

        order_total = Decimal(str(order_total))  

        if self.discount_type == 'fixed':
            return max(order_total - self.discount_value, Decimal('0'))  # Ensure total is not negative
        elif self.discount_type == 'percent':
            return max(order_total - (order_total * (self.discount_value / Decimal('100'))), Decimal('0'))
        return order_total

    def __str__(self):
        return self.code
