# Generated by Django 4.2.3 on 2023-07-26 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_remove_shipping_user_shipping_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shipping',
            name='email',
            field=models.EmailField(max_length=254),
        ),
    ]