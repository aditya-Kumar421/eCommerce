from django.db import models
from django.conf import settings
from products.models import Product
from coupons.models import Coupon
from decimal import Decimal
from django.conf import settings

ORDER_STATUS_CHOICES = (
    ('Pending', 'Pending'),
    ('Shipped', 'Shipped'),
    ('Delivered', 'Delivered')
)

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    total_amount = models.FloatField()
    discount_applied = models.FloatField(default=0.0)
    final_amount = models.FloatField()
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=10, choices=ORDER_STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # if self.pk:  # Ensure it's an update
        #     old_status = Order.objects.get(pk=self.pk).status
        #     if old_status != self.status:  # Check if status changed
        #         send_order_notification.delay(self.user.email, self.status)
        """Ensure the final amount is calculated correctly"""
        self.final_amount = Decimal(self.total_amount) - self.discount_applied  
        super().save(*args, **kwargs)

    def total_price(self):
        return sum(item.product.price * item.quantity for item in self.items.all())

    def __str__(self):
        return f"Order {self.id} by {self.user.username} - {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"
