# Generated by Django 4.2.3 on 2023-07-26 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_shipping_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='session_id',
            field=models.TextField(default='None'),
        ),
    ]