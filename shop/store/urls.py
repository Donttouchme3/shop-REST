from django.urls import path
from . import views

urlpatterns = [
     path('category/', views.CategoryViewSet.as_view({'get': 'list'})),
     path('category/<int:pk>/', views.CategoryViewSet.as_view({'get': 'retrieve'})),
     path('products/<int:pk>/', views.ProductViewSet.as_view({'get': 'retrieve'})),
     
     path('review/', views.ReviewCreateViewSet.as_view({'post': 'create'})),
     
     path('favorite/', views.AddToFavoriteViewSet.as_view({'post': 'create'})),
     path('my_favorite/', views.UserFavoriteProductsViewSet.as_view({'get': 'list'})),
     
     path('cart/add/', views.ProductToUserCartViewSet.as_view({'post': 'create'})),
     path('cart/delete/', views.ProductToUserCartViewSet.as_view({'post': 'create'})),
     path('cart/', views.UserCartViewSet.as_view({'get': 'list'})),
     
     path('checkout/', views.CheckoutView.as_view()),
     path('payment/', views.PaymentView.as_view({'post': 'create'})),
     path('my_orders/', views.UserOrderViewSet.as_view({'get': 'list'}))
     
     
]



#TODO исправить отзыв,  исправить показ избранных продуктов, корзина, страница пользователя
#TODO убрать permission для добавления в избранные и в корзину
#TODO отзыв: удалить, обновить
#TODO добавить рейтинги для продуктов