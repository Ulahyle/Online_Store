from celery import shared_task
from django.core.mail import send_mail
from order.models import Order


@shared_task
def send_order_confirmation_email(order_id):
    try:
        order = Order.objects.get(id=order_id)
        subject = f'Order Confirmation: {order.order_number}'
        message = f'Hi {order.customer.first_name},\n\nYour order has been placed successfully. Your order number is {order.order_number}.'
        from_email = 'no-reply@onlinestore.com'
        recipient_list = [order.customer.email]
        send_mail(subject, message, from_email, recipient_list)
        return f"Email sent for order {order_id}"
    except Order.DoesNotExist:
        return f"Order with ID {order_id} does not exist."
