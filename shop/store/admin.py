from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Product, Category, Gallery, Order, Cart, Shipping, FavoriteProduct

# Register your models here.
class AdminGalleryView(admin.TabularInline):
    fk_name = 'product'
    model = Gallery
    extra = 1

@admin.register(Category)
class AdminCategoryView(admin.ModelAdmin):
    list_display = ('id', 'title', 'parent', 'get_product_count')
    prepopulated_fields = {'slug': ('title',)}
    
    def get_product_count(self, obj):
        if obj.products:
            return str(len(obj.products.all()))
        else:
            return '0'

@admin.register(Product)
class AdminProductView(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'quantity', 'price', 'size', 'color', 'created_at', 'get_first_photo')
    list_editable = ('price', 'color', 'size', 'quantity')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('category', 'price')
    inlines = [AdminGalleryView]
    
    def get_first_photo(self, obj):
        if obj.images:
            try:
                return mark_safe(f'<img src="{obj.images.all()[0].image.url}" width="75"')
            except:
                return '-'
        else:
            return '-'
        
        
@admin.register(FavoriteProduct)
class AdminUserFavoriteProduct(admin.ModelAdmin):
    list_display = ('id', 'product')
        
@admin.register(Cart)
class AdminUserCart(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'price', 'quantity')
    list_filter = ('user',)
    
    
    
    
admin.site.register(Order)
admin.site.register(Shipping)
