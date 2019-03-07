from django.db import models
import math
from carts.models import Cart
from django.db.models.signals import pre_save, post_save
from ecommerce.generator import unique_order_id_generator

# Create your models here.

ORDER_STATUS_CHOICES = (
    ('created', 'Created'),
    ('paid', 'Paid'),
    ('shipped', 'Shipped'),
    ('refunded', 'Refunded'),
)



class Order(models.Model):
    order_id        = models.CharField(blank=True, max_length=120)
    # billing_profile
    # shipping_address
    # billing_address
    cart            = models.ForeignKey(Cart, on_delete=models.CASCADE)
    status          = models.CharField(max_length=120, default='created', choices=ORDER_STATUS_CHOICES)
    shipping_total  = models.DecimalField(max_digits=100, decimal_places=2, default=5.99)
    total           = models.DecimalField(max_digits=100, decimal_places=2, default=0.00)



    def __str__(self):
        return self.order_id

    def get_total(self):
        cart_total = self.cart.total
        shipping_total  = self.shipping_total
        new_total = math.fsum([cart_total, shipping_total])
        format_total = format(new_total, ".2f")
        self.total = format_total
        self.save()
        return new_total



### signals ###

# Generate Order ID :
def creating_order_id_automaticaly(sender, instance, *args, **kwargs):
    if not instance.order_id:
        instance.order_id = unique_order_id_generator(instance)

pre_save.connect(creating_order_id_automaticaly, sender=Order)

# Generate Total & Shipping Total :

def save_cart_total(sender, instance, created, *args, **kwargs):
    if not created:
        cart_total = instance.total
        cart_id = instance.id
        qs = Order.objects.filter(cart__id=cart_id)

        # if qs.count() == 1:                   # if there a problem u can use this code #
        #     order_obj = qs.first()
        #     order_obj.get_total()

post_save.connect(save_cart_total, sender=Cart)


def save_order_total(sender, instance, created, *args, **kwargs):
    if created:
        instance.get_total()

post_save.connect(save_order_total, sender=Order)
