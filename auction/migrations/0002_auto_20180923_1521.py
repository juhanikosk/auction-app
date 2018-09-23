# Generated by Django 2.1.1 on 2018-09-23 12:21

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auctionuser',
            name='first_name',
            field=models.CharField(max_length=128, validators=[django.core.validators.MinLengthValidator(3)], verbose_name='First name'),
        ),
        migrations.AlterField(
            model_name='auctionuser',
            name='last_name',
            field=models.CharField(max_length=128, validators=[django.core.validators.MinLengthValidator(3)], verbose_name='Last name'),
        ),
        migrations.AlterField(
            model_name='auctionuser',
            name='phone',
            field=models.CharField(max_length=28, validators=[django.core.validators.RegexValidator(message='Enter a valid phonenumber.', regex='^\\+?1?\\d{9,15}$')], verbose_name='Phonenumber'),
        ),
    ]