# Generated by Django 2.1.1 on 2018-10-05 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0007_auto_20181005_0838'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bid',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=6, verbose_name='Price'),
        ),
    ]