from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg
from .models import Product, Store, Category, PriceRecord
from .forms import ProductForm
import matplotlib.pyplot as plt
import io
import base64
import json
from datetime import timedelta, date

# Create your views here.

def home(request):
    # Calculate average price trend for the last 30 days
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    dates = []
    avg_prices = []
    
    current_date = start_date
    while current_date <= end_date:
        # Get average price of all records on this specific date
        avg_price = PriceRecord.objects.filter(date_recorded=current_date).aggregate(Avg('price'))['price__avg']
        
        dates.append(current_date.strftime('%Y-%m-%d'))
        # Handle None if no records for that day (just use previous or 0)
        if avg_price is not None:
             avg_prices.append(round(float(avg_price), 2))
        else:
             avg_prices.append(None) # Chart.js handles nulls by skipping or interpolating
             
        current_date += timedelta(days=1)

    context = {
        'chart_dates': json.dumps(dates),
        'chart_prices': json.dumps(avg_prices),
    }
    return render(request, 'home.html', context)

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


def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            return redirect('analytics-product-detail', pk=product.pk)
    else:
        form = ProductForm()
    return render(request, 'analytics/product_form.html', {'form': form, 'title': 'Добавить товар'})

def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('analytics-product-detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    return render(request, 'analytics/product_form.html', {'form': form, 'title': 'Редактировать товар'})
