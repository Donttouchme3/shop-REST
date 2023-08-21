# Generated by Django 4.2.3 on 2023-08-18 12:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0020_customer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='cart_product',
        ),
        migrations.CreateModel(
            name='OrderProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.product')),
            ],
            options={
                'verbose_name': 'Продукт заказа',
                'verbose_name_plural': 'Продукты заказа',
            },
        ),
    ]
