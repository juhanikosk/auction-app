from django.db import models
from django.shortcuts import reverse


class Item(models.Model):
    """
    Represents an item that can be auctioned.
    """
    class Meta:
        app_label="auction"

    name = models.CharField(blank=False, max_length=255, verbose_name="Name")
    description = models.CharField(blank=True, max_length=2048, verbose_name="Description")
    price = models.IntegerField(blank=False, verbose_name="Price")
    image = models.FileField(blank=True, verbose_name="Image")

    def get_absolute_url(self):
        return reverse('main-page')
