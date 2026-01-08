from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    slug = models.SlugField(unique=True, verbose_name="Слаг")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    description = models.TextField(blank=True, verbose_name="Описание")
    # Ensure Pillow is installed for ImageField
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Изображение")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.name

class Store(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    url = models.URLField(verbose_name="Ссылка")
    address = models.CharField(max_length=255, blank=True, verbose_name="Адрес")

    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = "Магазины"

    def __str__(self):
        return self.name

class PriceRecord(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name="Магазин")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    date_recorded = models.DateField(default=timezone.now, verbose_name="Дата записи")

    class Meta:
        verbose_name = "Запись о цене"
        verbose_name_plural = "Записи о ценах"

    def __str__(self):
        return f"{self.product.name} - {self.price} at {self.store.name}"

class ShoppingList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    products = models.ManyToManyField(Product, verbose_name="Товары")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"

    def __str__(self):
        return f"Shopping List for {self.user.username}"
