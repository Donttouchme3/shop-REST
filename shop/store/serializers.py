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
    class Meta:
        model = Product
        fields = ('id', 'title', 'price', 'slug', 'category', 'get_first_image',)
        
    def to_representation(self, instance):
        product_detail =  super().to_representation(instance)
        user = self.context['request'].user
        product = Product.objects.filter(id=instance.id).first()
        if user.is_authenticated:
            favorites = product.favorites.filter(user=user, product_id=product.id).first()
            product_in_cart = product.cart_product.filter(user=user, product_id=product.id).first()
            product_detail['favorites'] = favorites.id if favorites else False
            product_detail['product_in_cart'] = product_in_cart.id if product_in_cart else False
        return product_detail
        
        
class CategoryDetailSerializer(serializers.ModelSerializer):
    products = ProductsForCategories(many=True)
    class Meta:
        model = Category
        fields = ('id', 'title', 'image', 'slug', 'products')
        

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
            product_detail['favorites'] = favorites.id if favorites else False
            product_detail['product_in_cart'] = product_in_cart.id if product_in_cart else False
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
        if product and product.quantity >= quantity and quantity * product.price == price:
            if not product_in_cart:
                product_in_cart = Cart.objects.create(user=user, product_id=product_id, price=price, quantity=quantity)
                product.quantity -= quantity
                product.save()
            else:
                product_in_cart.quantity += quantity
                product_in_cart.price += price
                product.quantity -= quantity
                product_in_cart.save()
                product.save()
            return product_in_cart
        else: return None
        
        
        
            
    #     elif mixins.CART_DELETE_PRODUCT_PATH == path:
    #         if product_in_cart and not quantity:
    #             product.quantity += product_in_cart.quantity
    #             product.save()
    #             product_in_cart.delete()  
    #         elif product_in_cart and quantity and product_in_cart.quantity >= quantity:
    #             product_in_cart.quantity -= quantity
    #             product.quantity += quantity
    #             if product_in_cart.quantity > 0:
    #                 product_in_cart.price = product_in_cart.quantity * product.price
    #                 product_in_cart.save()
    #             else:
    #                 product_in_cart.delete()
    #             product.save()         

              
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
        
      
class UserOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = '__all__'
        
        
        

        
        
        
        
        
   

