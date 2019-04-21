from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.mail import send_mail
from django.template.loader import get_template

# Create your models here.

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


################################################################################

class GuestEmail(models.Model):
    email       = models.EmailField()
    active      = models.BooleanField(default=True)
    update      = models.DateTimeField(auto_now=True)
    timestamp   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
