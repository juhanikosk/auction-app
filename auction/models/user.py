from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core import validators


class AuctionUser(AbstractUser):
    first_name = models.CharField(verbose_name="First name", max_length=128, validators=[validators.MinLengthValidator(3)])
    last_name = models.CharField(verbose_name="Last name", max_length=128, validators=[validators.MinLengthValidator(3)])
    phone = models.CharField(verbose_name="Phonenumber", max_length=28, validators=[validators.RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Enter a valid phonenumber.")])

    def __str__(self):
        return "{} {} | {}".format(self.first_name, self.last_name, self.email)