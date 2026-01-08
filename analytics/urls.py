from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.products_list, name='analytics-products-list'),
    path('products/<int:pk>/', views.product_detail, name='analytics-product-detail'),
    path('products/create/', views.product_create, name='analytics-product-create'),
    path('products/<int:pk>/update/', views.product_update, name='analytics-product-update'),
    path('stores/', views.stores_list, name='analytics-stores-list'),
    path('dashboard/', views.dashboard, name='analytics-dashboard'),
    path('categories/', views.category_list, name='analytics-category-list'),
    path('categories/<str:slug>/', views.category_detail, name='analytics-category-detail'),
    path('data/import/', views.import_data, name='analytics-import-export'),
    path('data/export/', views.export_data, name='analytics-export-data'),
]
