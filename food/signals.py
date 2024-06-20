from django.db.models.signals import pre_save
from django.dispatch import receiver, Signal
from .models import Order,OrderItem

order_completed = Signal()

@receiver(order_completed)
def item_delete(sender,  instance, **kwargs):
    order_user = kwargs.get('user')
    order = Order.objects.get(id=instance.id, user=order_user)
    order_items = OrderItem.objects.filter(order=order)

    if order.completed:
        print('Order completed')
        # Example action: delete related order items
        order_items.delete()
    else:
        print('Order not completed')
        