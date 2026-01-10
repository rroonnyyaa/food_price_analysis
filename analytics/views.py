from django.shortcuts import render, get_object_or_404
from .models import Product, Store, Category

# Create your views here.

def home(request):
    return render(request, 'home.html')

def products_list(request):
    products = Product.objects.all().select_related('category')
    return render(request, 'analytics/products_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    # Fetch price history to show basic data
    price_history = product.pricerecord_set.all().order_by('-date_recorded')
    return render(request, 'analytics/product_detail.html', {
        'product': product,
        'price_history': price_history
    })

def stores_list(request):
    stores = Store.objects.all()
    return render(request, 'analytics/stores_list.html', {'stores': stores})

