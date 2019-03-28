from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .signals import object_viewed_signal
from .utils import client_ip
from accounts.signals import user_login_signals
# Create your models here.
User = settings.AUTH_USER_MODEL
# FORCE_SESSION_TO_ONE = getattr(settings, 'FORCE_SESSION_TO_ONE', False)
# FORCE_USER_SESSION = getattr(settings, 'FORCE_SESSION_TO_ONE', False)

class ObjectViewed(models.Model):
    user            = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    ip_address      = models.CharField(blank=True, null=True, max_length=220)
    content_type    = models.ForeignKey(ContentType, on_delete=models.CASCADE) # all models (product,carts,billing,order)
    object_id       = models.PositiveIntegerField()                            # user id, product_id, cart_id, order_id
    content_object  = GenericForeignKey('content_type', 'object_id')           # product instance
    timestamp       = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Object Viewed'
        verbose_name_plural = 'Object Viewed'



    def __str__(self):
        return f"{self.content_object} viewed on {self.timestamp}"




# Using signals created
@receiver(object_viewed_signal)
def object_viewed_resiver(sender, instance, request, *args, **kwargs):
    c_type = ContentType.objects.get_for_model(sender)
    view_obj = ObjectViewed.objects.create(
                user = request.user,
                content_type = c_type,
                object_id = instance.id,
                ip_address = client_ip(request)
    )

# object_viewed_signal.connect(object_viewed_resiver)


# do signal to make user login in one place only : user_login_signals



class UserSession(models.Model):
    user            = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    ip_address      = models.CharField(blank=True, null=True, max_length=220)
    session_key     = models.CharField(blank=True, null=True, max_length=200)
    timestamp       = models.DateTimeField(auto_now_add=True)
    active          = models.BooleanField(default=True)
    ended          = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)


    def end_session(self):
        session_key = self.session_key
        ended = self.ended
        try:
            Session.objects.get(pk=session_key).delete()
            self.active = False
            self.ended = True
            self.save()
        except:
            pass
        return self.ended


            ######### Signals #########

# @receiver(post_save, sender=UserSession)
# def session_reciver(sender, instance, created, *args, **kwargs):
#     if created:
#         qs = UserSession.objects.filter(user=instance.user, ended=False, active=False).exclude(id=instance.id)
#         for i in qs:
#             i.end_session()
#     if not instance.active and not instance.ended:
#         instance.end_session()



# @receiver(post_save, sender=User)
# def user_change_session_reciver(sender, instance, created, *args, **kwargs):
#     if created:
#         if instance.is_active == False:
#             qs = UserSession.objects.filter(user=instance.user, ended=False, active=False)
#             for i in qs:
#                 i.end_session()


                ########### signal to make user login #############

@receiver(user_login_signals)
def user_login_resiver(sender, instance, request, *args, **kwargs):
    user = instance
    ip_address = client_ip(request)
    session_key = request.session.session_key
    UserSession.objects.create(
            user = user,
            ip_address = ip_address,
            session_key = session_key,
    )
