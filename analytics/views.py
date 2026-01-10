from django.shortcuts import render, get_object_or_404
from .models import Product, Store, Category
import matplotlib.pyplot as plt
import io
import base64

# Create your views here.

def home(request):
    return render(request, 'home.html')

def products_list(request):
    products = Product.objects.all().select_related('category')
    return render(request, 'analytics/products_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    # Fetch price history sorted by date for the graph
    price_history = product.pricerecord_set.all().order_by('date_recorded')
    
    plot_url = None
    if price_history.exists():
        dates = [record.date_recorded for record in price_history]
        prices = [record.price for record in price_history]
        
        # Setup Matplotlib
        plt.switch_backend('AGG')
        fig = plt.figure(figsize=(10, 5))
        
        # Plot data
        plt.plot(dates, prices, marker='o', linestyle='-', color='#0d9488', linewidth=2)
        
        plt.title(f'Динамика цен: {product.name}', fontsize=14)
        plt.xlabel('Дата', fontsize=12)
        plt.ylabel('Цена (₽)', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save to buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        
        # Encode
        plot_url = base64.b64encode(image_png).decode('utf-8')
        plt.close(fig)

    # Reverse order for the table list (newest first)
    price_history_desc = price_history.reverse()

    return render(request, 'analytics/product_detail.html', {
        'product': product,
        'price_history': price_history_desc,
        'plot_url': plot_url
    })

def stores_list(request):
    stores = Store.objects.all()
    return render(request, 'analytics/stores_list.html', {'stores': stores})

