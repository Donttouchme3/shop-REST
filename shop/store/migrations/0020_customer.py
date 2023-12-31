# Generated by Django 4.2.3 on 2023-08-18 06:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0019_alter_cart_product_rating'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50, verbose_name='Имя пользователя')),
                ('last_name', models.CharField(max_length=50, verbose_name='Фамилия пользователя')),
                ('phone', models.CharField(max_length=30, verbose_name='Номер телефона')),
                ('image', models.ImageField(blank=True, null=True, upload_to='user/', verbose_name='Изображение')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
        ),
    ]
