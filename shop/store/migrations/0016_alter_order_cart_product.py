# Generated by Django 4.2.3 on 2023-07-26 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0015_alter_order_cart_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='cart_product',
            field=models.ManyToManyField(to='store.cart'),
        ),
    ]
