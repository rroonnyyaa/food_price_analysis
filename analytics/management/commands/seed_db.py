import random
import math
from datetime import timedelta, date
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from analytics.models import Category, Product, Store, PriceRecord

class Command(BaseCommand):
    help = 'Seeds the database with mock data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Wipe existing data before seeding',
        )

    def handle(self, *args, **kwargs):
        if kwargs['clean']:
            self.stdout.write('Cleaning existing data...')
            PriceRecord.objects.all().delete()
            Product.objects.all().delete()
            Store.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Data cleaned.'))
        
        if Product.objects.exists() and not kwargs['clean']:
            self.stdout.write(self.style.WARNING('Database contains data. Appending/Merging new data...'))

        self.stdout.write('Seeding database...')

        # Categories
        categories_data = [
            'Молочные продукты', 'Овощи и фрукты', 'Мясо и птица', 'Бакалея', 
            'Напитки', 'Хлеб и выпечка', 'Рыба и морепродукты'
        ]
        categories = {}
        for name in categories_data:
            cat, _ = Category.objects.get_or_create(
                name=name, 
                defaults={'slug': slugify(name, allow_unicode=True)}
            )
            categories[name] = cat

        # Stores
        stores_data = [
            {'name': 'Пятерочка', 'url': 'https://5ka.ru'},
            {'name': 'Магнит', 'url': 'https://magnit.ru'},
            {'name': 'Перекресток', 'url': 'https://perekrestok.ru'},
            {'name': 'ВкусВилл', 'url': 'https://vkusvill.ru'},
            {'name': 'Ашан', 'url': 'https://auchan.ru'},
            {'name': 'Лента', 'url': 'https://lenta.com'},
        ]
        stores = []
        for store_data in stores_data:
            store, _ = Store.objects.get_or_create(**store_data)
            stores.append(store)

        # Products (Name, Category Name, Approx Base Price)
        products_data = [
            ('Молоко Домик в деревне 3.2%', 'Молочные продукты', 90),
            ('Творог Простоквашино 5%', 'Молочные продукты', 120),
            ('Сыр Российский 200г', 'Молочные продукты', 250),
            ('Йогурт Чудо питьевой', 'Молочные продукты', 60),
            ('Сметана Брест-Литовск 15%', 'Молочные продукты', 85),
            
            ('Бананы Эквадор 1кг', 'Овощи и фрукты', 140),
            ('Картофель мытый 1кг', 'Овощи и фрукты', 45),
            ('Огурцы гладкие 1кг', 'Овощи и фрукты', 180),
            ('Томаты сливовидные 1кг', 'Овощи и фрукты', 220),
            ('Яблоки Гала 1кг', 'Овощи и фрукты', 110),
            ('Апельсины 1кг', 'Овощи и фрукты', 160),

            ('Куриное филе Петелинка 1кг', 'Мясо и птица', 380),
            ('Говядина тушеная банка', 'Мясо и птица', 250),
            ('Свинина лопатка 1кг', 'Мясо и птица', 420),
            ('Фарш Домашний 400г', 'Мясо и птица', 190),

            ('Макароны Макфа 450г', 'Бакалея', 65),
            ('Гречка Мистраль 900г', 'Бакалея', 85),
            ('Рис Краснодарский 900г', 'Бакалея', 95),
            ('Масло подсолнечное 1л', 'Бакалея', 130),
            ('Сахар 1кг', 'Бакалея', 70),

            ('Сок Добрый Яблоко 1л', 'Напитки', 120),
            ('Coca-Cola 0.9л', 'Напитки', 110),
            ('Вода Святой Источник 1.5л', 'Напитки', 40),

            ('Хлеб Бородинский', 'Хлеб и выпечка', 45),
            ('Батон Нарезной', 'Хлеб и выпечка', 35),
            ('Круассан 7days', 'Хлеб и выпечка', 100),
            
            ('Семга слабосоленая 200г', 'Рыба и морепродукты', 600),
            ('Креветки Королевские 1кг', 'Рыба и морепродукты', 800),
        ]
        
        products = []
        for name, cat_name, base_price in products_data:
            product, _ = Product.objects.get_or_create(
                name=name,
                category=categories[cat_name],
                defaults={'description': f'Вкусный и полезный продукт {name}'}
            )
            # Store base price in temporary storage on object for generation loop
            product.base_price_seed = base_price 
            products.append(product)

        # Price Records
        today = date.today()
        records_created = 0
        
        self.stdout.write(f'Generating price history for {len(products)} products...')
        
        for product in products:
            base_price = getattr(product, 'base_price_seed', 100)
            
            # Generate records for the last 90 days
            for day in range(90):
                current_date = today - timedelta(days=day)
                
                # Market trend (sine wave to simulate ups and downs over time)
                # Period of ~60 days approx
                trend = math.sin(day / 10.0) * (base_price * 0.15) 
                
                # Global inflation/deflation factor (linear)
                # Prices represent past, so 'day' represents how many days AGO.
                # If day=90 (90 days ago), price might be lower.
                # Let's say prices grow by 0.1% per day roughly
                inflation = base_price * (0.001 * (90 - day))
                
                daily_base_price = base_price + trend - inflation

                # For each store, try to create a record
                for store in stores:
                    # 80% chance a store has the item that day
                    if random.random() < 0.8: 
                        # Store specific pricing strategy:
                        # Perekrestok/VkusVill might be more expensive, 
                        # 5ka/Magnit cheaper.
                        
                        store_modifier = 1.0
                        if store.name in ['ВкусВилл', 'Перекресток']:
                            store_modifier = 1.15
                        elif store.name in ['Пятерочка', 'Магнит']:
                            store_modifier = 0.95
                        
                        # Random daily noise (-5% to +5%)
                        noise = random.uniform(-0.05, 0.05)
                        
                        final_price = daily_base_price * store_modifier * (1 + noise)
                        final_price = max(10, round(final_price, 2))

                        PriceRecord.objects.get_or_create(
                            product=product,
                            store=store,
                            date_recorded=current_date,
                            defaults={'price': final_price}
                        )
                        records_created += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded database. Created/Verified {records_created} price records.'))
