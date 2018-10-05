from django.db import models
from django.shortcuts import reverse

from auction.models import AuctionUser, Item


class BidManager(models.Manager):
    def get_queryset(self):
        return super(BidManager, self).get_queryset().filter(pending=False)


class BidPendingManager(models.Manager):
    def get_queryset(self):
        return super(BidPendingManager, self).get_queryset().filter(pending=True)


class Bid(models.Model):
    """
    Represents an item that can be auctioned.
    """
    class Meta:
        app_label="auction"

    user = models.ForeignKey(to="auction.AuctionUser", on_delete=models.CASCADE, related_name="bids")
    auction = models.ForeignKey(to=Item, on_delete=models.CASCADE, related_name="bids")
    price = models.DecimalField(blank=False, verbose_name="Price", max_digits=10, decimal_places=2)
    pending = models.BooleanField(verbose_name="Pending", default=True)

    objects = BidManager()
    pending_objects = BidPendingManager()

    def get_absolute_url(self):
        return reverse('main-page')
