from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver                ## Decorator
from accounts.models import GuestEmail
from django.urls import reverse
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

    def charge(self, order_obj, card=None):
        return Charge.objects.do(self, order_obj, card)

    def get_cards(self):
        qs = self.card_set.all()
        return qs

    @property
    def has_card(self):
        card_qs = self.get_cards()
        return card_qs.exists()

    @property
    def default_card(self):
        default_cards = self.get_cards().filter(active=True, default=True)
        if default_cards.exists():
            return default_cards.first()
        return None

    def get_payment_url(self):
        return reverse("billing:payment")

    def set_cards_inactive(self):
        cards = self.get_cards()
        cards.update(active=False)
        return cards.filter(active=True).count()


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

    def all(self, *args, **kwargs):
        return self.get_queryset().filter(active=True)

    def add_new(self, billing_profile, token):
        # if str(stripe_card_response.object) == "card":
        if token:
            stripe_card_response = stripe.Customer.create_source(billing_profile.customer_id,source=token)
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
    active              = models.BooleanField(default=True)
    timestamp           = models.DateTimeField(auto_now_add=True)


    objects = CardManager()

    def __str__(self):
        return "{} , {}".format(self.brand, self.last4)

### Card Signals ####


@receiver(post_save, sender=Card)
def new_card_receiver(sender, instance, created, *args, **kwargs):
    if instance.default:
        billing_profile = instance.billing_profile
        qs = Card.objects.filter(billing_profile=billing_profile).exclude(pk=instance.pk)
        qs.update(default=False)






### Charge Model ###
class ChargeManager(models.Manager):
    def do(self, billing_profile, order_obj, card=None):
        card_obj = card
        if card_obj is None:
            cards = billing_profile.card_set.filter(default=True)
            if cards.exists():
                card_obj = cards.first()
        if card_obj is None:
            return False, "No Cards Avaliable"

        c = stripe.Charge.create(
          amount = int(order_obj.total * 100),      # convert number to 39.31 -->> 3931
          currency ="usd",
          customer = billing_profile.customer_id,
          source = card_obj.stripe_id,              # obtained with Stripe.js
          metadata = {"order_id":order_obj.order_id}
        )

        new_charge_obj = self.model(
            billing_profile = billing_profile,
            stripe_id = c.id,
            paid = c.paid,
            refunded = c.refunded,
            outcome = c.outcome,
            outcome_type = c.outcome['type'],
            seller_message = c.outcome.get('seller_message'),
            risk_level = c.outcome.get('risk_level'),
        )
        new_charge_obj.save()
        return new_charge_obj.paid , new_charge_obj.seller_message

class Charge(models.Model):
    billing_profile     = models.ForeignKey(BillingProfile, on_delete=models.CASCADE)
    stripe_id           = models.CharField(max_length=120)
    paid                = models.BooleanField(default=False)
    refunded            = models.BooleanField(default=False)
    outcome             = models.TextField(null=True, blank=True)
    outcome_type        = models.CharField(max_length=120,null=True, blank=True)
    seller_message      = models.CharField(max_length=120,null=True, blank=True)
    risk_level          = models.CharField(max_length=120,null=True, blank=True)

    objects = ChargeManager()
