from django.db import models
from django.shortcuts import reverse

from auction.models import AuctionUser, Item


class Bid(models.Model):
    """
    Represents an item that can be auctioned.
    """
    class Meta:
        app_label="auction"

    user = models.ForeignKey(to="auction.AuctionUser", on_delete=models.CASCADE, related_name="bids")
    auction = models.ForeignKey(to=Item, on_delete=models.CASCADE, related_name="bids")
    price = models.DecimalField(blank=False, verbose_name="Price", max_digits=10, decimal_places=2)

    def get_absolute_url(self):
        return reverse('main-page')
