# Generated by Django 2.1.1 on 2018-10-05 06:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0009_auto_20181005_0921'),
    ]

    operations = [
        migrations.AddField(
            model_name='bid',
            name='pending',
            field=models.BooleanField(default=True, verbose_name='Pending'),
        ),
    ]
