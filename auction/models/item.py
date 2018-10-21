from django.db import models
from django.shortcuts import reverse

from django.utils.timezone import now

from auction.models import AuctionUser


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
    creator = models.ForeignKey(AuctionUser, on_delete=models.CASCADE, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('main-page')

    @property
    def get_top_price(self):
        if self.bids.count():
            return self.bids.all().order_by('-price')[0].price
        else:
            return self.price
