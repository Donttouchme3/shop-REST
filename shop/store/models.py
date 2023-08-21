from django.db import models
from django.contrib.auth.models import User
from . import mixins
import uuid
# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=200, verbose_name='Наименование категории')
    image = models.ImageField(upload_to='category/', null=True, blank=True, verbose_name='Изображение')
    slug = models.SlugField(unique=True, verbose_name='Уникальный идентификатор')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, 
                               null=True, blank=True, related_name='subcategories', verbose_name='Категория')
    
    def __str__(self):
        return self.title
    
    def get_image(self):
        if self.image:
            return self.image.url
        else:
            return 'https://www.raumplus.ru/upload/iblock/545/Skoro-zdes-budet-foto.jpg'

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    

class Product(models.Model):
    title = models.CharField(max_length=200, verbose_name='Наименование продукта')
    description = models.TextField(default='Описание продукта', verbose_name='Описание продукта')
    quantity = models.PositiveIntegerField(default=0, verbose_name='Количество на складе')
    price = models.PositiveIntegerField(verbose_name='Цена продукта', default=0)
    size = models.CharField(max_length=200, verbose_name='Размер продукта')
    color = models.CharField(max_length=200, default='Серебро', verbose_name='Цвет продукта')
    slug = models.SlugField(unique=False, verbose_name='Уникальный идентификатор продукта')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления продукта')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория', related_name='products')
    
    def __str__(self):
        return self.title

    
    def get_first_image(self):
        if self.images:
            try:
                return self.images.first().image.url
            except:
                return 'https://www.raumplus.ru/upload/iblock/545/Skoro-zdes-budet-foto.jpg'
        else:
            return 'https://www.raumplus.ru/upload/iblock/545/Skoro-zdes-budet-foto.jpg'
        
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    
        
class Gallery(models.Model):
    image = models.ImageField(upload_to='product/', verbose_name='Изображение продукта')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    
    def __str__(self):
        return self.product.title
    
    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Галерея изображений'
        
        

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    text = models.TextField(verbose_name='Отзыва пользователя')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания отзыва')
    product = models.ForeignKey(Product, related_name='reviews', verbose_name='Продукт', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    
    def __str__(self):
        return self.product.title

    class Meta:
        verbose_name ='Отзыв'
        verbose_name_plural = 'Отзывы'
        
        
class Rating(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE, related_name='user_rating')
    product = models.ForeignKey(Product, verbose_name='Продукт', on_delete=models.CASCADE, related_name='product_rating')
    star = models.CharField(choices=mixins.get_star(), verbose_name='Оценка')
    
    def __str__(self) -> str:
        return f'Оценка пользователя: {self.user.username}'
    
    class Meta:
        verbose_name = 'Рейтинг'
        verbose_name_plural = 'Рейтинги'
        
        
class FavoriteProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продукт', related_name='favorites')
    
    def __str__(self):
        return self.product.title
    
    
    class Meta:
        verbose_name ='Избранный продукт'
        verbose_name_plural = 'Избранные продукты'
        

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_product')
    quantity = models.PositiveIntegerField(default=0, verbose_name='Количество продукта')
    price = models.PositiveIntegerField()
    
    def __str__(self):
        return str(self.id)
    
    class Meta:
        verbose_name ='Корзина'
        verbose_name_plural = 'Корзины'
        
    
class Shipping(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50, default='+998')
    address = models.CharField(max_length=200)
    
    def __str__(self):
        return str(self.id)
    
    class Meta:
        verbose_name = 'Личная информация'
        verbose_name_plural = 'Личные информации'


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shipping = models.ForeignKey(Shipping, on_delete=models.PROTECT)
    order_total_price = models.PositiveIntegerField()
    order_product_total_quantity = models.PositiveIntegerField()
    session_id = models.TextField(unique=True)
    
    def __str__(self):
        return str(self.pk)
    
    class Meta:
        verbose_name ='Заказ'
        verbose_name_plural = 'Заказы'
        
class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return str(self.order.id)
    
    class Meta:
        verbose_name = 'Продукт заказа'
        verbose_name_plural = 'Продукты заказа'
        
    
        
        
class Customer(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    first_name = models.CharField(verbose_name='Имя пользователя', max_length=50)
    last_name = models.CharField(verbose_name='Фамилия пользователя', max_length=50)
    phone = models.CharField(verbose_name='Номер телефона', max_length=30)
    image = models.ImageField(verbose_name='Изображение', upload_to='user/', null=True, blank=True)
        
        

    
    
    