from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.products_list, name='analytics-products-list'),
    path('products/<int:pk>/', views.product_detail, name='analytics-product-detail'),
    path('stores/', views.stores_list, name='analytics-stores-list'),
]
