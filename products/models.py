from django.db import models
from django.db.models.signals import pre_save, post_save
from django.urls import reverse
from .manager import ProductManager
from products.utils import unique_slug_generator
from .fileupload import upload_image_path
# Create your models here.

class Product(models.Model):
    title           = models.CharField(max_length=120)
    slug            = models.SlugField(blank=True,unique=True)
    description     = models.TextField()
    price           = models.DecimalField(decimal_places=2, max_digits=20, default=11.11)
    image           = models.ImageField(upload_to=upload_image_path, null=True, blank=True)
    featured        = models.BooleanField(default=False)
    active          = models.BooleanField(default=True)
    timestamp       = models.DateTimeField(auto_now_add=True)

    objects = ProductManager()

    def get_absolute_url(self):
        return reverse("products:detail", kwargs={"slug":self.slug})


    def __str__(self):
        return self.title










## Slug signals

def creating_slug_automaticaly(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(creating_slug_automaticaly, sender=Product)
