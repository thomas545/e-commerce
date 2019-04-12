from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .utils import Mailchimp
# Create your models here.

User = settings.AUTH_USER_MODEL


class MarketingPreference(models.Model):
    user                    = models.OneToOneField(User, on_delete=models.CASCADE)
    subscribed              = models.BooleanField(default=True)
    mailchimp_subscribed    = models.NullBooleanField(blank=True)
    mailchimp_msg           = models.TextField(blank=True, null=True)
    timestamp               = models.DateTimeField(auto_now_add=True)
    updated                 = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.user.email




## signals ##

@receiver(post_save, sender=MarketingPreference)
def create_marketing_receiver(sender, instance, created, *args, **kwargs):
    if created:
        status_code, response_data = Mailchimp().subscribe(instance.user.email)


@receiver(pre_save, sender=MarketingPreference)
def update_marketing_receiver(sender, instance, *args, **kwargs):
    if instance.subscribed != instance.mailchimp_subscribed:
        if instance.subscribed:
            status_code , response_data = Mailchimp().subscribe(instance.user.email)
        else:
            status_code , response_data = Mailchimp().unsubscribe(instance.user.email)

        if response_data['status'] == 'subscribed':
            instance.subscribed = True
            instance.mailchimp_subscribed = True
            instance.mailchimp_msg = response_data
        else:
            instance.subscribed = False
            instance.mailchimp_subscribed = False
            instance.mailchimp_msg = response_data





@receiver(post_save, sender=User)
def make_marketing_receiver(sender, instance, created, *args, **kwargs):
    if created:
        MarketingPreference.objects.get_or_create(user=instance)
