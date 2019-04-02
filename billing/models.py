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
STRIPE_PUB_KEY = 'pk_test_kC38CxS6Zu5j3HANr0FIkvgZ'


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


############## Stripe Model ###############

class CardManager(models.Manager):
    def add_new(self, billing_profile, stripe_card_response):
        if str(stripe_card_response.object) == "card":
            new_card = self.model(
                billing_profile = billing_profile,
                stripe_id = stripe_card_response.id,
                brand = stripe_card_response.brand,
                country = stripe_card_response.country,
                exp_month = stripe_card_response.exp_month,
                exp_year = stripe_card_response.exp_year,
                last4 = stripe_card_response.last4
            )

            new_card.save()
            return new_card
        return None

class Card(models.Model):
    billing_profile     = models.ForeignKey(BillingProfile, on_delete=models.CASCADE)
    stripe_id           = models.CharField(max_length=120)
    brand               = models.CharField(max_length=120, blank=True, null=True)
    country             = models.CharField(max_length=20, blank=True, null=True)
    exp_month           = models.IntegerField(blank=True, null=True)
    exp_year            = models.IntegerField(blank=True, null=True)
    last4               = models.CharField(max_length=4, blank=True, null=True)
    default             = models.BooleanField(default=True)


    objects = CardManager()

    def __str__(self):
        return "{} , {}".format(self.brand, self.last4)
