from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import reverse

from auction.models import Item


class Bid(models.Model):
    """
    Represents an item that can be auctioned.
    """
    class Meta:
        app_label="auction"

    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="bids")
    auction = models.ForeignKey(to=Item, on_delete=models.CASCADE, related_name="bids")
    price = models.IntegerField(blank=False, verbose_name="Price")

    def get_absolute_url(self):
        return reverse('main-page')
