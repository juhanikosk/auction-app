# Generated by Django 2.1.1 on 2018-10-24 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0014_item_deadline'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='price',
            field=models.FloatField(verbose_name='Price'),
        ),
    ]