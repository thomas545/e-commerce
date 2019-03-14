from django.db import models
import math
from carts.models import Cart
from addresses.models import Address
from billing.models import BillingProfile
from django.db.models.signals import pre_save, post_save
from ecommerce.generator import unique_order_id_generator

# Create your models here.

ORDER_STATUS_CHOICES = (
    ('created', 'Created'),
    ('paid', 'Paid'),
    ('shipped', 'Shipped'),
    ('refunded', 'Refunded'),
)


class OrderManager(models.Manager):
    def new_or_get(self, billing_profile, cart_obj):
        created = False
        qs = self.get_queryset().filter(cart=cart_obj, billing_profile=billing_profile, active=True)
        if qs.count() == 1:
            obj = qs.first()
        else:
            obj = self.model.objects.create(cart=cart_obj, billing_profile=billing_profile)
            created = True
        return obj, created

class Order(models.Model):
    billing_profile     = models.ForeignKey(BillingProfile, null=True, blank=True, on_delete=models.CASCADE)
    order_id            = models.CharField(blank=True, max_length=120)
    shipping_address    = models.ForeignKey(Address, related_name='shipping_address', null=True, blank=True, on_delete=models.CASCADE)
    billing_address     = models.ForeignKey(Address, related_name='billing_address', null=True, blank=True, on_delete=models.CASCADE)
    cart                = models.ForeignKey(Cart, on_delete=models.CASCADE)
    status              = models.CharField(max_length=120, default='created', choices=ORDER_STATUS_CHOICES)
    shipping_total      = models.DecimalField(max_digits=100, decimal_places=2, default=5.99)
    total               = models.DecimalField(max_digits=100, decimal_places=2, default=0.00)
    active              = models.BooleanField(default=True)

    objects = OrderManager()

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
    qs = Order.objects.filter(cart=instance.cart).exclude(billing_profile=instance.billing_profile)
    if qs.exists():
        qs.update(active=False)

pre_save.connect(creating_order_id_automaticaly, sender=Order)

# Generate Total & Shipping Total :

def save_cart_total(sender, instance, created, *args, **kwargs):
    if not created:
        cart_total = float(instance.total)
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
