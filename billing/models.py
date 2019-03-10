from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver                ## Decorator
# Create your models here.

class BillingProfile(models.Model):
    user        = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    email       = models.EmailField()
    active      = models.BooleanField(default=True)
    update      = models.DateTimeField(auto_now=True)
    timestamp   = models.DateTimeField(auto_now_add=True)
    # customer_id  for stripe payment


    def __str__(self):
        return self.email




## Signals ##

# # for customerID
# @receiver(post_save, sender=User)
# def billing_created_receiver(sender, instance, created, *args, **kwargs):
#     if created:
#         instance.customer_id = newID
#         instance.save()


# Create With User like profile
# @receiver(post_save, sender=User)
def user_created_receiver(sender, instance, created, *args, **kwargs):
    if created and instance.email:
        BillingProfile.objects.get_or_create(user=instance, email=instance.email)

post_save.connect(user_created_receiver, sender=User)
