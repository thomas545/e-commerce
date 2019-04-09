from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
# Create your models here.

User = settings.AUTH_USER_MODEL


class MarketingPreference(models.Model):
    user            = models.OneToOneField(User, on_delete=models.CASCADE)
    subscribed      = models.BooleanField(default=True)
    mailchimp_msg   = models.TextField(blank=True, null=True)
    timestamp       = models.DateTimeField(auto_now_add=True)
    update          = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.user.email




## signals ##

@receiver(post_save, sender=MarketingPreference)
def marketing_update_receiver(sender, instance, created, *args, **kwargs):
    if created:
        pass
        print("Add User To Mailchimp")




@receiver(post_save, sender=User)
def make_marketing_receiver(sender, instance, created, *args, **kwargs):
    if created:
        MarketingPreference.objects.get_or_create(user=instance)
