from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.mail import send_mail
from django.template.loader import get_template
from django.conf import settings
from django.urls import reverse
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from ecommerce.generator import unique_key_generator
# Create your models here.
# User = settings.AUTH_USER_MODEL
# send_mail(subject, message, from_email, recipint_list, html_message)

class UserManager(BaseUserManager):
    def create_user(self, email, full_name=None, password=None, is_active=True, is_staff=False, is_admin=False):
        if not email:
            raise ValueError("User Must Have E-mail")
        if not password:
            raise ValueError("User Must Have Password")
        user_obj = self.model(email=self.normalize_email(email), full_name=full_name)
        user_obj.set_password(password)
        user_obj.staff  = is_staff
        user_obj.admin  = is_admin
        user_obj.is_active = is_active
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, email, full_name=None, password=None):
        user = self.create_user(
            email,
            full_name=full_name,
            password = password,
            is_staff=True
        )
        return user

    def create_superuser(self, email, full_name=None, password=None):
        user = self.create_user(
            email,
            full_name=full_name,
            password = password,
            is_staff=True,
            is_admin=True
        )
        return user



## Custom User Model ##

class User(AbstractBaseUser):
    email       = models.EmailField(max_length=200, unique=True)
    full_name   = models.CharField(max_length=200, blank=True, null=True)
    is_active   = models.BooleanField(default=True)  # can Login
    staff       = models.BooleanField(default=False)  # staff user
    admin       = models.BooleanField(default=False)  # Super User
    timestamp   = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email' # Username
    REQUIRED_FIELDS = []

    objects = UserManager()


    def __str__(self):
        return self.email

    def get_full_name(self):
        if  self.full_name:
            return self.full_name
        return self.email

    def get_short_name(self):
        return self.email

    def has_perm(self, perm, obj=None):   # built in method for permission admin
        return True

    def has_module_perms(self, app_label):        # built in method for permission admin
        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    # @property
    # def is_active(self):
    #     return self.active


## model for activation email ##

DEFAULT_ACTIVATION_DAYS = getattr(settings, 'DEFAULT_ACTIVATION_DAYS', 7) # for default days

class EmailActivationQuerySet(models.query.QuerySet):  # QuerySet for using in manager
    def confirm(self):
        now = timezone.now()
        start_range = now - timedelta(days=DEFAULT_ACTIVATION_DAYS)
        end_range = now
        return self.filter(
            activated=False,
            forced_expired=False
            ).filter(
                timestamp__gt=start_range,
                timestamp__lte=end_range
            )


class EmailActivationManager(models.Manager): # EmailActivation Model Manager
    # for looping all get_queryset in EmailActivationQuerySet
    def get_queryset(self):
        return EmailActivationQuerySet(self.model, using=self._db)

    # for Email Activation Manager (EmailActivationManager.objects.confirmable())
    def confirmable(self):
        return self.get_queryset().confirm()


class EmailActivation(models.Model):
    user                = models.ForeignKey(User, on_delete=models.CASCADE)
    email               = models.EmailField()
    key                 = models.CharField(blank=True, max_length=200, null=True)
    activated           = models.BooleanField(default=False)
    forced_expired      = models.BooleanField(default=False)
    expires             = models.IntegerField(default=7)
    timestamp           = models.DateTimeField(auto_now_add=True)
    update              = models.DateTimeField(auto_now=True)

    objects = EmailActivationManager()

    def __str__(self):
        return self.email

    def can_activate(self):
        qs = EmailActivation.objects.filter(pk=self.pk).confirm()
        if qs.exists():
            return True
        return False

    def activate(self):
        if self.can_activate():
            # this equal pre_save signal
            user = self.user
            user.is_active = True
            user.save()
            # this equal post_save signal
            self.activated = True
            self.save()
            return True
        return False


    def regenerate(self):
        self.key = None
        self.save()
        if self.key is not None:
            return True
        return False

    def send_activation(self):
        if not self.activated and not self.forced_expired:
            if self.key:
                base_url = getattr(settings, 'BASE_URL', None)
                path_key = reverse("accounts:activate", kwargs={'key':self.key})
                path = "{base}{path}".format(base=base_url, path=path_key)
                context = {
                    'path': path,
                    'email': self.email
                }
                txt_ = get_template('registration/emails/verify.txt').render(context)
                html_ = get_template('registration/emails/verify.html').render(context)
                subject = '1-click Email Activation'
                from_email = settings.DEFAULT_FROM_EMAIL
                recipint_list = [self.email]
                sent_email = send_mail(
                    subject,
                    txt_,
                    from_email,
                    recipint_list,
                    html_message = html_,
                    fail_silently = False,
                )
                return sent_email
        return False

## Signals ##

@receiver(pre_save, sender=EmailActivation)
def pre_save_email_activation(sender, instance, *args, **kwargs):
    if not instance.activated and not instance.forced_expired:
        if not instance.key:
            instance.key = unique_key_generator(instance)



@receiver(post_save, sender=User)
def post_save_email_activation(sender, instance, created, *args, **kwargs):
    if created:
        obj = EmailActivation.objects.create(user=instance, email=instance.email)
        obj.send_activation()


###Guest Email Model###

class GuestEmail(models.Model):
    email       = models.EmailField()
    active      = models.BooleanField(default=True)
    update      = models.DateTimeField(auto_now=True)
    timestamp   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
