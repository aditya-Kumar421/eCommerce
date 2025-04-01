from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_order_notification(email, order_status):
    subject = "Order Status Update"
    message = f"Your order status has been updated to: {order_status}"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
    return f"Notification sent to {email}"