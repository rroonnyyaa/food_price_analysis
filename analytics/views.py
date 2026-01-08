from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg, Min, Max, Count, F, Q
from django.db.models.functions import TruncDay
from .models import Product, Store, Category, PriceRecord
from .forms import ProductForm
import json
import csv
import pandas as pd
from django.http import HttpResponse
from django.contrib import messages
from datetime import timedelta, date, datetime
from .utils import get_market_inflation, get_price_forecast

# Create your views here.
def export_data(request):
    # Export logic
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="price_records.csv"'

    writer = csv.writer(response)
    writer.writerow(['Product', 'Category', 'Store', 'Price', 'Date'])

    records = PriceRecord.objects.all().select_related('product', 'product__category', 'store')
    for record in records:
        writer.writerow([
            record.product.name,
            record.product.category.name,
            record.store.name,
            record.price,
            record.date_recorded
        ])

    return response

def import_data(request):
    if request.method == 'POST' and request.FILES['file']:
        csv_file = request.FILES['file']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Пожалуйста, загрузите CSV файл')
            return redirect('analytics-import-export')
        
        try:
            df = pd.read_csv(csv_file)
            # Expected columns: Product, Category, Store, Price, Date
            
            records_created = 0
            for index, row in df.iterrows():
                # Get or create category
                category, _ = Category.objects.get_or_create(
                    name=row['Category'],
                    defaults={'slug': row['Category'].lower().replace(' ', '-')}
                )
                
                # Get or create product
                product, _ = Product.objects.get_or_create(
                    name=row['Product'],
                    category=category
                )
                
                # Get or create store
                store, _ = Store.objects.get_or_create(
                    name=row['Store'],
                    defaults={'url': 'http://example.com'}
                )
                
                # Create price record
                date_obj = datetime.strptime(row['Date'], '%Y-%m-%d').date() if isinstance(row['Date'], str) else row['Date']
                
                PriceRecord.objects.get_or_create(
                    product=product,
                    store=store,
                    price=row['Price'],
                    date_recorded=date_obj
                )
                records_created += 1
                
            messages.success(request, f'Успешно импортировано {records_created} записей')
        except Exception as e:
            messages.error(request, f'Ошибка при импорте: {str(e)}')
            
    return render(request, 'analytics/import_export.html')

def dashboard(request):
    # Filters
    selected_days = int(request.GET.get('days', 30))
    selected_store_id = request.GET.get('store', '')
    selected_category_id = request.GET.get('category', '')
    
    end_date = date.today()
    start_date = end_date - timedelta(days=selected_days)
    
    # 1. Market Inflation (Basket Analysis)
    inflation_data = get_market_inflation(days=selected_days)
    
    # 2. Daily Store Activity (Filtered)
    records_query = PriceRecord.objects.filter(date_recorded__gte=start_date)
    if selected_store_id:
        records_query = records_query.filter(store_id=selected_store_id)
    if selected_category_id:
        records_query = records_query.filter(product__category_id=selected_category_id)
        
    # Chart: Average Price by Store (Dynamic)
    stores = Store.objects.all()
    chart_datasets = []
    
    # Generate labels for X axis
    date_labels = []
    current = start_date
    while current <= end_date:
        date_labels.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=1)
        
    colors = ['#0d9488', '#dc2626', '#2563eb', '#d97706', '#7c3aed', '#db2777']
    
    for i, store in enumerate(stores):
        # Skip if store filter is active and doesn't match
        if selected_store_id and str(store.id) != selected_store_id:
            continue
            
        daily_prices = records_query.filter(store=store)\
            .annotate(day=TruncDay('date_recorded'))\
            .values('day')\
            .annotate(avg_price=Avg('price'))\
            .order_by('day')
            
        price_map = {}
        for item in daily_prices:
            # Handle date/string variations from DB
            d_val = item['day']
            key = d_val[:10] if isinstance(d_val, str) else d_val.strftime('%Y-%m-%d')
            price_map[key] = round(float(item['avg_price']), 2)
            
        data_points = [price_map.get(d, None) for d in date_labels]
        
        chart_datasets.append({
            'label': store.name,
            'data': data_points,
            'borderColor': colors[i % len(colors)],
            'backgroundColor': 'transparent',
            'borderWidth': 2,
            'tension': 0.3,
            'spanGaps': True,
            'pointRadius': 2
        })

    # 3. Store Basket Comparison (Cheapest Store)
    store_basket = []
    for store in stores:
        # Calculate for ALL products regardless of filter to get true store value, 
        # OR apply category filter if user wants "Cheapest store for Dairy"
        basket_query = PriceRecord.objects.filter(store=store, date_recorded__gte=start_date)
        if selected_category_id:
             basket_query = basket_query.filter(product__category_id=selected_category_id)
             
        latest_prices = {}
        # Fetch and process in python to ensure 'latest'
        for record in basket_query.order_by('date_recorded'):
            latest_prices[record.product_id] = record.price
            
        if latest_prices:
            basket_sum = sum(latest_prices.values())
            
            product_count = len(latest_prices)
            avg_item_price = basket_sum / product_count
            
            store_basket.append({
                'name': store.name,
                'total': round(basket_sum, 2),
                'count': product_count,
                'avg_item_price': round(avg_item_price, 2)
            })
    
    store_basket.sort(key=lambda x: x['avg_item_price'])

    return render(request, 'analytics/dashboard.html', {
        'store_basket': store_basket,
        'total_products': Product.objects.count(),
        'total_records': PriceRecord.objects.count(),
        'chart_labels': json.dumps(date_labels),
        'chart_datasets': json.dumps(chart_datasets),
        'inflation_dates': json.dumps(inflation_data['dates']),
        'inflation_prices': json.dumps(inflation_data['prices']),
        'inflation_change': inflation_data['change'],
        'stores': stores,
        'categories': Category.objects.all(),
        'selected_days': selected_days,
        'selected_store': int(selected_store_id) if selected_store_id else None,
        'selected_category': int(selected_category_id) if selected_category_id else None,
    })

def category_list(request):
    # Fix: Use 'product' as the related name based on field error feedback
    categories = Category.objects.annotate(product_count=Count('product')).all()
    return render(request, 'analytics/category_list.html', {'categories': categories})

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.product_set.all()
    
    # Category Price Index (Avg price of category per day)
    # Only for last 90 days
    start_date = date.today() - timedelta(days=90)
    daily_stats = PriceRecord.objects.filter(
        product__category=category,
        date_recorded__gte=start_date
    ).annotate(day=TruncDay('date_recorded')).values('day').annotate(avg_price=Avg('price')).order_by('day')
    
    dates = [stat['day'].strftime('%Y-%m-%d') for stat in daily_stats]
    prices = [round(float(stat['avg_price']), 2) for stat in daily_stats]

    return render(request, 'analytics/category_detail.html', {
        'category': category,
        'products': products,
        'chart_dates': json.dumps(dates),
        'chart_prices': json.dumps(prices),
    })

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
    
    dates = []
    prices = []
    
    if price_history.exists():
        dates = [record.date_recorded.strftime('%Y-%m-%d') for record in price_history]
        prices = [float(record.price) for record in price_history]

    # Reverse order for the table list (newest first)
    price_history_desc = price_history.reverse()

    # Calculate Forecast
    forecast = get_price_forecast(product.id, days_ahead=30)

    return render(request, 'analytics/product_detail.html', {
        'product': product,
        'price_history': price_history_desc,
        'chart_dates': json.dumps(dates),
        'chart_prices': json.dumps(prices),
        'forecast': forecast,
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
