from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from shop import settings
import stripe

from .serializers import (CategorySerializer, CategoryDetailSerializer, ProductDetailSerializer,
                          CreateReviewSerializer, UserFavoriteProductSerializer, AddProductToUserFavorites,
                          AddProductToUserCartSerializer, UserCartSerializer, ShippingSerializer, UserOrderSerializer)
from .models import (Category, Product, FavoriteProduct,
                    Cart, Shipping, Order)
from . import mixins



class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CategoryDetailSerializer
        elif self.action == 'list':
            return CategorySerializer
    

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer      
    
class ReviewCreateViewSet(viewsets.ModelViewSet):
    serializer_class = CreateReviewSerializer  
    permission_classes = [permissions.IsAuthenticated]  
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user) 
        
        
class AddToFavoriteViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]  
    serializer_class = AddProductToUserFavorites
    queryset = Product.objects.all()


class UserFavoriteProductsViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]  
    serializer_class = UserFavoriteProductSerializer 

    def get_queryset(self):
        user = self.request.user  
        products = FavoriteProduct.objects.filter(user=user) 
        return products
    
    
class ProductToUserCartViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Product.objects.all()
    serializer_class = AddProductToUserCartSerializer
    
    
    

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
            
            mixins.create_order(user=user,
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
        
