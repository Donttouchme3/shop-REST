from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from shop import settings
import stripe

from .serializers import (CategorySerializer, CategoryDetailSerializer, ProductDetailSerializer,
                          ReviewCUDSerializer, UserFavoriteProductSerializer, AddProductToUserFavorites,
                          AddProductToUserCartSerializer, ShippingSerializer, UserOrderSerializer,
                          UserCartSerializer, RatingSerializer, CustomerSerializer, PaymentSerializer, 
                          ProductsForCategories)
from .models import (Category, Product, FavoriteProduct,
                    Cart, Shipping, Order, Review, Customer)
from . import mixins



class CustomerViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CustomerSerializer
    queryset = Customer
    lookup_field = 'user'
    
    def perform_create(self, serializer):
        return super().perform_create(serializer.save(user=self.request.user))

class CategoryProductsPagination(PageNumberPagination):
    page_size = 10  
    page_size_query_param = 'page_size'
    max_page_size = 100

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CategoryDetailSerializer
        elif self.action == 'list':
            return CategorySerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        products = instance.products.all()  
        paginator = CategoryProductsPagination()
        page = paginator.paginate_queryset(products, request)
        if page is not None:
            serializer = ProductsForCategories(page, context={'request': self.request}, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ProductsForCategories(products,  context={'request': self.request}, many=True)
        return Response(serializer.data)

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

        
class RatingViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RatingSerializer
    
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
    lookup_field = 'product'
    
    def get_queryset(self):
        if self.action == 'create':
            return Product.objects.all()
        elif mixins.CART_CHANGE_PRODUCT_QUANTITY_IN_CART_PATH or mixins.CART_DELETE_PRODUCT_PATH in self.request.path:
            return Cart.objects.all()
    
    def perform_destroy(self, instance):
        product_in_cart = Cart.objects.get(id=instance.id)
        product = Product.objects.get(id=product_in_cart.product.id)
        product.quantity += product_in_cart.quantity
        product.save()        
        return super().perform_destroy(instance)
    
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


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
    
    def create(self, request):
        serializer = PaymentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        else: return Response(status=status.HTTP_400_BAD_REQUEST)
    

class UserOrderViewSet(viewsets.ModelViewSet):
    serializer_class = UserOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user=user)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['action'] = self.action 
        return context

        
