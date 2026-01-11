import random
from datetime import timedelta, date
from django.core.management.base import BaseCommand
from analytics.models import Category, Product, Store, PriceRecord

class Command(BaseCommand):
    help = 'Seeds the database with mock data'

    def handle(self, *args, **kwargs):
        if Product.objects.exists():
            self.stdout.write(self.style.SUCCESS('Database already contains data. Skipping seed.'))
            return

        self.stdout.write('Seeding database...')

        # Categories
        categories_data = ['Молочные продукты', 'Овощи и фрукты', 'Мясо и птица', 'Бакалея']
        categories = []
        for name in categories_data:
            cat, _ = Category.objects.get_or_create(name=name, slug=name.lower().replace(' ', '-'))
            categories.append(cat)

        # Stores
        stores_data = [
            {'name': 'Пятерочка', 'url': 'https://5ka.ru'},
            {'name': 'Магнит', 'url': 'https://magnit.ru'},
            {'name': 'Перекресток', 'url': 'https://perekrestok.ru'},
        ]
        stores = []
        for store_data in stores_data:
            store, _ = Store.objects.get_or_create(**store_data)
            stores.append(store)

        # Products
        products_data = [
            ('Молоко Домик в деревне 3.2%', 0),
            ('Творог Простоквашино 5%', 0),
            ('Бананы Эквадор', 1),
            ('Картофель мытый', 1),
            ('Куриное филе Петелинка', 2),
            ('Говядина тушеная', 2),
            ('Макароны Макфа', 3),
            ('Гречка Мистраль', 3),
        ]
        
        products = []
        for name, cat_idx in products_data:
            product, _ = Product.objects.get_or_create(
                name=name,
                category=categories[cat_idx],
                description=f'Вкусный и полезный продукт {name}'
            )
            products.append(product)

        # Price Records
        today = date.today()
        for product in products:
            base_price = random.randint(50, 500)
            for day in range(30):
                current_date = today - timedelta(days=day)
                # Create random price fluctuation
                price = base_price + random.randint(-20, 20)
                store = random.choice(stores)
                
                PriceRecord.objects.create(
                    product=product,
                    store=store,
                    price=price,
                    date_recorded=current_date
                )

        self.stdout.write(self.style.SUCCESS('Successfully seeded database with mock data'))
