from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver                ## Decorator
from accounts.models import GuestEmail
# Create your models here.
User = settings.AUTH_USER_MODEL

import stripe
stripe.api_key = "sk_test_gnVSg3SSbYKxbTbPesQwsoTv"



class BillingProfileManager(models.Manager):
    def new_or_get(self, request):
        user = request.user
        guest_email_id = request.session.get("guest_email_id")
        created = False
        obj = None
        if user.is_authenticated:
            obj, created = self.model.objects.get_or_create(user=user, email=user.email)
        elif guest_email_id is not None:
            guest_email_obj = GuestEmail.objects.get(id=guest_email_id)
            obj, created = self.model.objects.get_or_create(email=guest_email_obj.email)
        else:
            pass
        return obj, created


class BillingProfile(models.Model):
    user        = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    email       = models.EmailField()
    active      = models.BooleanField(default=True)
    update      = models.DateTimeField(auto_now=True)
    timestamp   = models.DateTimeField(auto_now_add=True)
    customer_id = models.CharField(max_length=200, blank=True, null=True)
    # customer_id  for stripe payment

    objects = BillingProfileManager()

    def __str__(self):
        return self.email




## Signals ##

# for customerID Stripe Payment
@receiver(pre_save, sender=BillingProfile)
def billing_created_payment_id_receiver(sender, instance, *args, **kwargs):
    if not instance.customer_id and instance.email:
        print("Request was sent to stripe")
        customer = stripe.Customer.create(email=instance.email)
        print(customer)
        instance.customer_id = customer.id


# Create With User like profile
# @receiver(post_save, sender=User)
def user_created_receiver(sender, instance, created, *args, **kwargs):
    if created and instance.email:
        BillingProfile.objects.get_or_create(user=instance, email=instance.email)

post_save.connect(user_created_receiver, sender=User)
