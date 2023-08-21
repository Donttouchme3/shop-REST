from django.urls import path
from . import views

urlpatterns = [
     path('category/', views.CategoryViewSet.as_view({'get': 'list'})),
     path('category/<int:pk>/', views.CategoryViewSet.as_view({'get': 'retrieve'})),
     path('products/<int:pk>/', views.ProductViewSet.as_view({'get': 'retrieve'})),
     
     path('review/', views.ReviewCUDViewSet.as_view({'post': 'create'})),
     path('review/<int:pk>/update/', views.ReviewCUDViewSet.as_view({'patch': 'partial_update'})),
     path('review/<int:pk>/delete/', views.ReviewCUDViewSet.as_view({'delete': 'destroy'})),
     
     path('rating/', views.RatingViewSet.as_view({'post': 'create'})),
     
     path('favorite/add/', views.AddToFavoriteViewSet.as_view({'post': 'create'})),
     path('favorite/delete/<int:pk>/', views.DeleteProductFromFavoriteViewSet.as_view({'delete': 'destroy'})),
     path('my_favorite/', views.UserFavoriteProductsViewSet.as_view({'get': 'list'})),
     
     path('cart/add/', views.ProductCUDUserCartViewSet.as_view({'post': 'create'})),
     path('cart/<int:product>/delete/', views.ProductCUDUserCartViewSet.as_view({'delete': 'destroy'})),
     path('cart/<int:product>/update/', views.ProductCUDUserCartViewSet.as_view({'put': 'update'})),
     path('cart/', views.UserCartViewSet.as_view({'get': 'list'})),
     
     path('checkout/', views.UserCartViewSet.as_view({'get': 'list'})),
     path('payment/', views.PaymentView.as_view({'post': 'create'})),
     
     
     path('customer/', views.CustomerViewSet.as_view({'post': 'create'})),
     path('customer/<int:user>/update/', views.CustomerViewSet.as_view({'patch': 'partial_update'})),     
     path('customer/<int:user>/', views.CustomerViewSet.as_view({'get': 'retrieve'})),
     
     path('my_orders/', views.UserOrderViewSet.as_view({'get': 'list'})),
     path('my_orders/<uuid:pk>/', views.UserOrderViewSet.as_view({'get': 'retrieve'}))
     
     
]


