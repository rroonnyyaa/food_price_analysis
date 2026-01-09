from crudbuilder.abstract import BaseCrudBuilder
from .models import Product, Store, Category, ShoppingList, PriceRecord

class ProductCrud(BaseCrudBuilder):
    model = Product
    search_fields = ['name', 'description']
    tables2_fields = ('name', 'category', 'description', 'image')
    tables2_css_class = "table table-bordered table-condensed"
    tables2_pagination = 20  # pagination sure!
    modelform_excludes = []
    login_required = True
    permission_required = False

class StoreCrud(BaseCrudBuilder):
    model = Store
    search_fields = ['name', 'address']
    tables2_fields = ('name', 'url', 'address')
    tables2_css_class = "table table-bordered table-condensed"
    modelform_excludes = []
    login_required = True

class CategoryCrud(BaseCrudBuilder):
    model = Category
    search_fields = ['name']
    tables2_fields = ('name', 'slug')
    tables2_css_class = "table table-bordered table-condensed"
    modelform_excludes = []
    login_required = True

class ShoppingListCrud(BaseCrudBuilder):
    model = ShoppingList
    search_fields = ['user__username']
    tables2_fields = ('user', 'created_at')
    tables2_css_class = "table table-bordered table-condensed"
    modelform_excludes = []
    login_required = True

class PriceRecordCrud(BaseCrudBuilder):
    model = PriceRecord
    search_fields = ['product__name', 'store__name']
    tables2_fields = ('product', 'store', 'price', 'date_recorded')
    tables2_css_class = "table table-bordered table-condensed"
    modelform_excludes = []
    login_required = True
