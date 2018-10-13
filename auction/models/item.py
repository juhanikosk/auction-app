from django.db import models
from django.shortcuts import reverse


class ItemManager(models.Manager):
    def get_queryset(self):
        return super(ItemManager, self).get_queryset().filter(pending=False)


class ItemPendingManager(models.Manager):
    def get_queryset(self):
        return super(ItemPendingManager, self).get_queryset().filter(pending=True)


class Item(models.Model):
    """
    Represents an item that can be auctioned.
    """
    class Meta:
        app_label="auction"

    name = models.CharField(blank=False, max_length=255, verbose_name="Name")
    description = models.CharField(blank=True, max_length=2048, verbose_name="Description")
    price = models.DecimalField(blank=False, verbose_name="Price", max_digits=10, decimal_places=2)
    image = models.FileField(blank=True, null=True, verbose_name="Image")
    pending = models.BooleanField(verbose_name="Pending", default=True)

    objects = ItemManager()
    pending_objects = ItemPendingManager()

    def get_absolute_url(self):
        return reverse('main-page')

    @property
    def get_top_price(self):
        if self.bids.count():
            return self.bids.all().order_by('-price')[0].price
        else:
            return self.price
