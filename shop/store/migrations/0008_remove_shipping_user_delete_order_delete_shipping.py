# Generated by Django 4.2.3 on 2023-07-26 10:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_shipping_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shipping',
            name='user',
        ),
        migrations.DeleteModel(
            name='Order',
        ),
        migrations.DeleteModel(
            name='Shipping',
        ),
    ]
