from django.contrib.auth.models import AbstractUser
from django.db import models


class AuctionUser(AbstractUser):
    first_name = models.CharField(verbose_name="First name", max_length=128)
    last_name = models.CharField(verbose_name="Last name", max_length=128)
    phone = models.CharField(verbose_name="Phonenumber", max_length=28)

    def __str__(self):
        return "{} {} | {}".format(self.first_name, self.last_name, self.email)