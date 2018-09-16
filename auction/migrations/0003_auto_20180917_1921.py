# Generated by Django 2.1.1 on 2018-09-17 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0002_newsitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='image',
            field=models.FileField(blank=True, upload_to='', verbose_name='Image'),
        ),
        migrations.AlterField(
            model_name='item',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='item',
            name='price',
            field=models.IntegerField(verbose_name='Price'),
        ),
    ]