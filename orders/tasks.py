# cart/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Order

@shared_task
def send_order_status_email(order_id, user_email):
    order = Order.get_by_id(order_id)
    if not order:
        return {"error": "Order not found"}
    
    subject = f"Order {order['_id']} Status Update"
    message = f"Dear Customer,\n\nYour order (ID: {order['_id']}) status has been updated to '{order['status']}'.\n\nTotal Amount: ${order['final_amount']}\n\nThank you for shopping with us!"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]
    
    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=False,
    )
    return {"status": f"Email sent for order {order['_id']} to {user_email}"}