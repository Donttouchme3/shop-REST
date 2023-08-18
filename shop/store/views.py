from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from shop import settings
import stripe

from .serializers import (CategorySerializer, CategoryDetailSerializer, ProductDetailSerializer,
                          ReviewCUDSerializer, UserFavoriteProductSerializer, AddProductToUserFavorites,
                          AddProductToUserCartSerializer, ShippingSerializer, UserOrderSerializer,
                          UserCartSerializer)
from .models import (Category, Product, FavoriteProduct,
                    Cart, Shipping, Order, Review)
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
    
    
class ReviewCUDViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewCUDSerializer  
    permission_classes = [permissions.IsAuthenticated]  
    
    def get_queryset(self):
        user = self.request.user
        review_id = self.kwargs['pk'] if 'pk' in self.kwargs else None
        user_review = Review.objects.filter(user=user, id=review_id).exists() if review_id else False
        if user_review: return Review.objects.all()
        else: return None
        
    def perform_create(self, serializer):
        serializer.save(user=self.request.user) 

        
        
        
class AddToFavoriteViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]  
    serializer_class = AddProductToUserFavorites
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        

class DeleteProductFromFavoriteViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = FavoriteProduct.objects.all()
    

class UserFavoriteProductsViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]  
    serializer_class = UserFavoriteProductSerializer 

    def get_queryset(self):
        user = self.request.user  
        products = FavoriteProduct.objects.filter(user=user) 
        return products
    
    
    
    
class ProductCUDUserCartViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AddProductToUserCartSerializer
    
    def get_queryset(self):
        if self.action == 'create':
            return Product.objects.all()
        elif self.action == 'destroy':
            return Cart.objects.all()
    
    def perform_destroy(self, instance):
        product_in_cart = Cart.objects.get(id=instance.id)
        product = Product.objects.get(id=product_in_cart.product.id)
        product.quantity += product_in_cart.quantity
        product.save()        
        return super().perform_destroy(instance)


class UserCartViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserCartSerializer
    
    def get_queryset(self):
        user = self.request.user
        return Cart.objects.filter(user=user)
    
    def finalize_response(self, request, response, *args, **kwargs):
        queryset = self.get_queryset()
        serializer_data = self.get_serializer(queryset, many=True).data
        cart_total_price = sum([product.price for product in queryset])
        cart_product_total_quantity =sum([product.quantity for product in queryset])
        final_data = {
            'products': serializer_data,
            'totals': {'total_price': cart_total_price, 'total_quantity': cart_product_total_quantity}
        }
        if mixins.CHECKOUT_PATH == self.request.path:
            user_shipping_data = Shipping.objects.filter(user=self.request.user).first()
            shipping_serializer = ShippingSerializer(user_shipping_data)
            final_data['user_shipping_data'] = shipping_serializer.data if user_shipping_data else 'None'
        response =  Response(final_data, status=status.HTTP_200_OK)
        return super().finalize_response(request, response)
            
        
class PaymentView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    def list(self, request):
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
    serializer_class = UserOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user=user)
    

        
