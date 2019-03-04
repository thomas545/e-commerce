from django.db import models
from django.db.models import Q
# creating model managers

class ProductQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(active=True)

    def featured(self):
        return self.filter(featured=True)

    def search(self, query):
        search_fields = (
        Q(title__icontains=query)| Q(description__icontains=query)|
        Q(tag__title__icontains=query))
        return self.filter(search_fields).distinct()

class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)


    def all(self):
        return self.get_queryset().active()


    def featured(self):
        return self.get_queryset().featured()


    def search(self, query):
        return self.get_queryset().active().search(query)
