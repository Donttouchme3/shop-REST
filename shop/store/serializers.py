from rest_framework import serializers
from .models import Product, Category, Review, FavoriteProduct, Order, Cart, Shipping
from . import mixins


class CategoryFilterSerializer(serializers.ListSerializer):
    def to_representation(self, obj):
        obj = obj.filter(parent=None)
        return super().to_representation(obj) 

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
    favorites = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ('id', 'title', 'price', 'slug', 'category', 'get_first_image', 'favorites')
        
    def get_favorites(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            favorites = obj.favorites.filter(user=user, product_id=obj.id).exists()
            return favorites
        else:
            return False
        
        
class CategoryDetailSerializer(serializers.ModelSerializer):
    products = ProductsForCategories(many=True)
    class Meta:
        model = Category
        fields = ('id', 'title', 'image', 'slug', 'products')
        

class CreateReviewSerializer(serializers.ModelSerializer):
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
    
    
class AddProductToUserFavorites(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id',)
        
    def save(self, **kwargs):
        product_id = self.context['request'].data['id']
        user = self.context['request'].user
        if Product.objects.filter(id=product_id).exists():
            favorite, created = FavoriteProduct.objects.get_or_create(user=user, product_id=product_id)
            if created:
                created
            else:
                favorite.delete()
            
                 
class UserFavoriteProductSerializer(serializers.ModelSerializer):
    product = ProductsForCategories()
    
    class Meta:
        model = FavoriteProduct
        fields = ('product',)

    
class ProductDetailSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field='title', read_only=True)
    reviews = ReviewSerializer(many=True)
    favorites = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_favorites(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.favorites.filter(user=user, product_id=obj.id).exists()
        else:
            return False
  
class AddProductToUserCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(required=False)
    price = serializers.IntegerField(required=False)
      
    def save(self, **kwargs):
        user = self.context['request'].user
        data = self.context['request'].data
        path = self.context['request'].path
        product_id = data['product_id']
        quantity = int(data['quantity']) if 'quantity' in data else None
        price = int(data['price']) if 'price' in data else None
        product = Product.objects.filter(id=product_id).first()
        product_in_cart = Cart.objects.filter(user=user, product_id=product_id).first()
        
        if mixins.CART_ADD_PRODUCT_PATH == path:
            if product and product.quantity >= quantity and quantity * product.price == price:
                if not product_in_cart:
                    Cart.objects.update_or_create(user=user, product_id=product_id, price=price, quantity=quantity)
                    product.quantity -= quantity
                    product.save()
                else:
                    product_in_cart.quantity += quantity
                    product_in_cart.price += price
                    product.quantity -= quantity
                    product_in_cart.save()
                    product.save()
        elif mixins.CART_DELETE_PRODUCT_PATH == path:
            if product_in_cart and not quantity:
                product.quantity += product_in_cart.quantity
                product.save()
                product_in_cart.delete()  
            elif product_in_cart and quantity and product_in_cart.quantity >= quantity:
                product_in_cart.quantity -= quantity
                product.quantity += quantity
                if product_in_cart.quantity > 0:
                    product_in_cart.price = product_in_cart.quantity * product.price
                    product_in_cart.save()
                else:
                    product_in_cart.delete()
                product.save()
                 
         
         

              
              
class UserCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        exclude = ('id', 'user')
        
        
class ShippingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipping
        exclude = ('id', 'user')
        
    
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
                
class UserOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        
        
        
        
        
   

