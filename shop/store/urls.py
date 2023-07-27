from django.urls import path
from . import views

urlpatterns = [
     path('category/', views.CategoryViewSet.as_view({'get': 'list'})),
     path('category/<int:pk>/', views.CategoryViewSet.as_view({'get': 'retrieve'})) ,
     path('products/', views.ProductViewSet.as_view({'get': 'list'})),
     path('products/<int:pk>/', views.ProductViewSet.as_view({'get': 'retrieve'})),
     path('review/', views.ReviewCreateViewSet.as_view({'post': 'create'})),
     path('favorite/<int:pk>/', views.AddToFavoriteViewSet.as_view({'get': 'retrieve'})),
     path('my_favorite/', views.UserFavoriteProductsViewSet.as_view({'get': 'list'})),
     path('add_to_cart/<int:pk>/', views.AddProductToUserCartViewSet.as_view({'get': 'retrieve'})),
     path('add_to_cart/<int:pk>/<str:action>/', views.AddProductToUserCartViewSet.as_view({'get': 'retrieve'})),
     path('my_cart/', views.UserCartViewSet.as_view({'get': 'list'})),
     path('my_cart/delete/', view=views.UserCartViewSet.as_view({'get': 'delete'})),
     path('checkout/', views.CheckoutView.as_view()),
     path('payment/', views.PaymentView.as_view({'post': 'create'})),
     path('my_orders/', views.UserOrderViewSet.as_view({'get': 'list'}))
     
     
]



#TODO исправить отзыв, показ изображений в продукте, исправить показ избранных продуктов, корзина, страница пользователя