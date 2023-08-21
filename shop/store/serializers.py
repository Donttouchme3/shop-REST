from rest_framework import serializers
from .models import Product, Category, Review, FavoriteProduct, Order, Cart, Shipping, Rating, Customer, OrderProduct
from . import mixins
from shop import settings
import stripe

class CategoryFilterSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        data = data.filter(parent=None)
        return super().to_representation(data) 

class CategoryRecursiveSerializer(serializers.Serializer):
    def to_representation(self, instance):
        serializer = self.parent.parent.__class__(instance, context=self.context)
        return serializer.data

class CategorySerializer(serializers.ModelSerializer):
    subcategories = CategoryRecursiveSerializer(many=True)
    
    class Meta:
        list_serializer_class = CategoryFilterSerializer
        model = Category
        fields = '__all__'


        
class ProductsForCategories(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'title', 'price', 'slug', 'category', 'get_first_image',)
        
    def to_representation(self, instance):
        product_detail =  super().to_representation(instance)
        user = self.context['request'].user
        product = Product.objects.filter(id=instance.id).first()
        if user.is_authenticated:
            favorites = product.favorites.filter(user=user, product_id=product.id).first()
            product_detail['favorite'] = True if favorites else False
        return product_detail
        

class CategoryDetailSerializer(serializers.ModelSerializer):
    products = ProductsForCategories(many=True)
    class Meta:
        model = Category
        fields = ('id', 'title', 'image', 'slug', 'products')
        list_serializer_class = mixins.ProductPagination
        

class ReviewCUDSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        exclude = ('user',)        
        

class ReviewFilterSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        data = data.filter(parent=None)
        return super().to_representation(data)
    

class RecursiveReviewSerializer(serializers.Serializer):
    def to_representation(self, instance):
        serializer = self.parent.parent.__class__(instance, context=self.context)
        return serializer.data  


class ReviewSerializer(serializers.ModelSerializer):
    children = RecursiveReviewSerializer(many=True)
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    
    class Meta:
        list_serializer_class = ReviewFilterSerializer
        model = Review
        fields = ('id','user', 'text', 'created_at', 'children')
        
        
class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        exclude = ('user',)
        
    def create(self, validated_data):
        create, _ = Rating.objects.update_or_create(
            user = validated_data.get('user'),
            product = validated_data.get('product'),
            defaults={'star': validated_data.get('star')}
        )
        return create
    
    
class AddProductToUserFavorites(serializers.ModelSerializer):
    class Meta:
        model = FavoriteProduct
        exclude = ('user',)

    def create(self, validated_data):
        product_id = validated_data.get('product')
        user = validated_data.get('user')
        favorite_product, _ = FavoriteProduct.objects.get_or_create(user=user, product=product_id)
        return favorite_product
            
                 
class UserFavoriteProductSerializer(serializers.ModelSerializer):
    product = ProductsForCategories()
    
    class Meta:
        model = FavoriteProduct
        fields = ('product',)
        
        

    
class ProductDetailSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field='title', read_only=True)
    reviews = ReviewSerializer(many=True)

    class Meta:
        model = Product
        fields = '__all__'
        
    def to_representation(self, instance):
        product_detail =  super().to_representation(instance)
        user = self.context['request'].user
        product = Product.objects.filter(id=instance.id).first()
        if user.is_authenticated:
            favorites = product.favorites.filter(user=user, product_id=product.id).first()
            product_in_cart = product.cart_product.filter(user=user, product_id=product.id).first()
            user_product_rating = product.product_rating.filter(user=user, product_id=product.id).first()
            product_detail['favorite'] = favorites.id if favorites else False
            product_detail['in_cart'] = product_in_cart.id if product_in_cart else False
            product_detail['rating'] = user_product_rating.star if user_product_rating else False
            product_detail['image'] = product.get_first_image()
        return product_detail
    
  
class AddProductToUserCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        exclude = ('user',)    
    
    def create(self, validated_data):
        user = self.context['request'].user
        product_id = validated_data.get('product').id
        quantity = validated_data.get('quantity')
        price = validated_data.get('price')
        product = Product.objects.filter(id=product_id).first()
        product_in_cart = Cart.objects.filter(user=user, product=product_id).first()
        if product and product.quantity >= quantity and product.price == price:
            if not product_in_cart:
                product_in_cart = Cart.objects.create(user=user, product_id=product_id, price=price * quantity, quantity=quantity)
                product.quantity -= quantity
                product.save()
            else:
                product_in_cart.quantity += quantity
                product_in_cart.price += price * quantity
                product.quantity -= quantity
                product_in_cart.save()
                product.save()
            return product_in_cart
        else: product_in_cart
        
    def update(self, instance, validated_data):
        product_in_cart = instance
        product = validated_data.get('product')
        quantity = validated_data.get('quantity')
        price = validated_data.get('price')
        user = validated_data.get('user')
        if product.price == price and product_in_cart.product == product and product_in_cart.user == user:
            mixins.update_product_quantity(product_in_cart, product, quantity)
            product_in_cart.quantity = quantity
            product_in_cart.price = quantity * price
            product_in_cart.save()
        return product_in_cart

                 
              
class UserCartSerializer(serializers.ModelSerializer):
    product = ProductsForCategories()
    class Meta:
        model = Cart
        exclude = ('user',)
        

class ShippingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipping
        exclude = ('user',)
    
    def create(self, validated_data):
        data, _ = Shipping.objects.update_or_create(
            user=validated_data.get('user'),
            defaults={
                'first_name': validated_data.get('first_name'),
                'last_name': validated_data.get('last_name'),
                'address': validated_data.get('address'),
                'phone': validated_data.get('phone'),
                'email': validated_data.get('email')
            }
        )
        return data
    
    
class CustomerSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        customer = super().to_representation(instance)
        customer['user'] = self.context['request'].user.id
        return customer
    class Meta:
        model = Customer
        exclude = ('user',)
        
    
class PaymentSerializer(serializers.Serializer):
    card = serializers.CharField(required=True)
    cvs = serializers.CharField(required=True)
    active_to = serializers.CharField(required=True)
    save = serializers.SerializerMethodField()
    
    def get_save(self, obj):
        request = self.context.get('request')
        user = request.user
        stripe.api_key = settings.STRIPE_SECRET_KEY
        user_cart = Cart.objects.filter(user=user)
        user_data = Shipping.objects.filter(user=user).first()
        total_price = sum([product.price for product in user_cart])
        total_quantity = sum([product.quantity for product in user_cart])
        if total_price > 0 and user_data:
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
            if session:
                order = Order.objects.create(user=user,
                            shipping=user_data,
                            order_total_price=total_price,
                            order_product_total_quantity=total_quantity,
                            session_id=session['id']) 
                for cart_product in user_cart:            
                    order_product = OrderProduct.objects.create(order=order, product=cart_product.product)
                if order:
                    user_cart.delete()
                return True
        else:
            if total_price == 0:
                return 'Ваша корзина пуста'
            elif not user_data:
                return 'Вы не указали адрес доставки'
               
               

class UserOrderSerializer(serializers.ModelSerializer):
    shipping = ShippingSerializer()
    
    def to_representation(self, instance):
        context = super().to_representation(instance)
        if self.context['action'] == 'retrieve':   
            order_products = OrderProduct.objects.filter(order_id=instance.id)
            products = []
            for order_product in order_products:
                order_product_serializer = ProductsForCategories(order_product.product, context={'request': self.context['request']})
                products.append(order_product_serializer.data)
            context['products'] = products
            return context
        else: return context
    

    class Meta:
        model = Order
        fields = '__all__'
        
    
        
        
        

        
        
        
        
        
   

