from rest_framework import serializers
from .models import Product, Category, Review, FavoriteProduct, Order, Cart, Shipping
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
        fields = ('id','title', 'subcategories')
        
        
class CategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'title', 'price')
        

class ProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'title', 'price')
        

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
        fields = ('user', 'text', 'created_at', 'children')
        
        
class UserFavoriteProductSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    product = serializers.SlugRelatedField(slug_field='title', read_only=True)
    
    class Meta:
        model = FavoriteProduct
        fields = ('user', 'product')        
 
        
class ProductDetailSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field='title', read_only=True)
    reviews = ReviewSerializer(many=True)
    favorite = serializers.BooleanField()

    class Meta:
        model = Product
        fields = '__all__'
        
        
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
        
        
        
        
        
   

