from typing import Any
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django.db import models
from rest_framework import status
from rest_framework.views import APIView
from shop import settings
import stripe

from .serializers import (CategorySerializer, CategoryDetailSerializer,
                          ProductsSerializer, ProductDetailSerializer,
                          CreateReviewSerializer, UserFavoriteProductSerializer,
                          UserCartSerializer, ShippingSerializer, UserOrderSerializer)
from .models import (Category, Product, FavoriteProduct,
                    Cart, Shipping, Order)
from .mixins import create_order



class CategoryViewSet(viewsets.ViewSet):
    
    def retrieve(self, request, *args, **kwargs):
        category_id = kwargs['pk']  
        products = Product.objects.filter(category_id=category_id)  
        serializer = CategoryDetailSerializer(products, many=True)  
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        categories = Category.objects.all()  
        serializer = CategorySerializer(categories, many=True)  
        return Response(serializer.data)
    

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        if self.action == 'list':
            return Product.objects.all()
        elif self.action == 'retrieve':
            return Product.objects.all().annotate(
                favorite = models.Count('favorites', filter=models.Q(favorites__user=self.request.user, favorites__product_id=self.kwargs['pk'])
            ))

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductsSerializer  
        elif self.action == 'retrieve':
            return ProductDetailSerializer  
        
        
    
class ReviewCreateViewSet(viewsets.ModelViewSet):
    serializer_class = CreateReviewSerializer  
    permission_classes = [permissions.IsAuthenticated]  
    def perform_create(self, serializer):
        serializer.save(user=self.request.user) 
        
        
class AddToFavoriteViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]  
    
    def retrieve(self, request, *args, **kwargs):
        product_id = kwargs['pk']  
        user = self.request.user  
        fav_product = FavoriteProduct.objects.filter(user=user, product_id=product_id).first()

        if fav_product:
            fav_product.delete()
            return Response({'message': 'Продукт успешно удален из избранных продуктов'}, status=200)
        else:
            FavoriteProduct.objects.create(user=user, product_id=product_id)
            return Response({'message': 'Продукт успешно добавлен в избранные продукты'}, status=201)


class UserFavoriteProductsViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]  
    serializer_class = UserFavoriteProductSerializer 

    def get_queryset(self):
        user = self.request.user  
        products = FavoriteProduct.objects.filter(user=user) 
        return products
    
    
class AddProductToUserCartViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def retrieve(self, request, action=None, *args, **kwargs):
        user = request.user
        MIN_PRODUCT_QUANTITY = 1
        product = Product.objects.get(pk=self.kwargs['pk'])
        cart_product = Cart.objects.filter(product=product, user=user).first()
        
        if not action:
            if cart_product:
                product.quantity += cart_product.quantity
                product.save()
                cart_product.delete()
                return Response({'message': 'Продукт успешно удален из корзины'}, status=204)
            else:   
                Cart.objects.create(product=product, user=user, quantity=MIN_PRODUCT_QUANTITY, price=product.price)
                product.quantity -= MIN_PRODUCT_QUANTITY
                message = 'Продукт успешно добавлен в корзину'
        elif action == 'add' and cart_product:
            cart_product.quantity = models.F('quantity') + 1
            product.quantity = models.F('quantity') - 1
        elif action == 'delete' and cart_product:
            if cart_product.quantity > MIN_PRODUCT_QUANTITY:
                cart_product.quantity = models.F('quantity') - 1
                product.quantity = models.F('quantity') + 1
            else:
                product.quantity = models.F('quantity') + 1
                product.save()
                cart_product.delete()
                return Response({'message': 'Продукт успешно удален из корзины'}, status=204)
        if cart_product:
            cart_product.price = cart_product.quantity * product.price
            
        product.save()
        cart_product.save() if cart_product else None
        return Response({'message': message if 'message' in locals() else 'Количество продуктов успешно изменено'}, status=200)
    

class UserCartViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Cart.objects.filter(user=user)
        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = UserCartSerializer(queryset, many=True)
        cart_total_price = sum([product.price for product in queryset])
        cart_product_total_quantity =sum([product.quantity for product in queryset])
        return Response({'products': serializer.data, 'total_price': cart_total_price, 'total_quantity': cart_product_total_quantity}, status=200)
    
    def delete(self, request):
        self.get_queryset().delete()
        return Response({'message': 'Ваша корзина очищена!'}, status=204)
    
    
class CheckoutView(APIView):
    
    def cart_data(self, request):
        user = request.user
        queryset = Cart.objects.filter(user=user)
        cart_total_price = sum([product.price for product in queryset])
        cart_product_total_quantity =sum([product.quantity for product in queryset])
        return {'queryset': queryset, 
                'cart_total_price': cart_total_price, 
                'cart_product_total_quantity': cart_product_total_quantity, 
                'user': user}
    
    def get(self, request):
        cart_data = self.cart_data(request)
        user_data = Shipping.objects.filter(user=cart_data['user']).first()
        if user_data:
            user_serializer = ShippingSerializer(user_data)
            
        serializer = UserCartSerializer(cart_data['queryset'], many=True)
        return Response({'products': serializer.data,
                         'user_data': user_serializer.data if user_data else 'Увы! мы не знаем куда доставить ваш заказ', 
                         'total_price': cart_data['cart_total_price'], 
                         'total_quantity': cart_data['cart_product_total_quantity']}, 
                        status=status.HTTP_200_OK)
        
    def post(self, request):
        cart_data = self.cart_data(request)
        user = cart_data['user']
        cart_serializer = UserCartSerializer(cart_data['queryset'], many=True)

        serializer = ShippingSerializer(data=self.request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response({'Detail': serializer.data,
                             'Cart': {'Products' : cart_serializer.data, 
                                      'Общая стоимость': cart_data['cart_total_price'], 
                                      'Общее количество продуктов': cart_data['cart_product_total_quantity']}}, 
                            status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Возникла ошибка'}, status=status.HTTP_400_BAD_REQUEST)
        
        
class PaymentView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    
    def create(self, request):
        user = self.request.user
        user_cart = Cart.objects.filter(user=user)
        user_data = Shipping.objects.filter(user=user).first()
        total_price = sum([product.price for product in user_cart])
        total_quantity = sum([product.quantity for product in user_cart])
        if total_price > 0 and total_quantity >= 1 and user_data:
            session = stripe.checkout.Session.create(
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Товары'
                        },
                        'unit_amount': int(total_price / 2)
                    },
                    'quantity': total_quantity,
                    
                }],
                mode='payment',
                success_url=request.build_absolute_uri(),
                cancel_url=request.build_absolute_uri()
            )
            
            create_order(user=user,
                         total_price=total_price,
                         total_quantity=total_quantity,
                         session_id=session['id'],
                         shipping=user_data,
                         cart_product=[cart_product.product.id for cart_product in user_cart])
            
            user_cart.delete()
            
            return Response({'message': 'Заказ оформлен'}, status=status.HTTP_303_SEE_OTHER)
        elif total_quantity < 1:
            return Response({'error': 'Ваша корзина пуста'}, status=status.HTTP_409_CONFLICT)
        else:
            return Response({'error': 'Вы не указали адрес доставки'})


class UserOrderViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.filter(user=user)
        return queryset
    
    serializer_class = UserOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
        
