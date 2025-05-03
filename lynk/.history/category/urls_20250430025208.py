from django.urls import path
from .views import *

app_name = 'category'

urlpatterns = [
    path('', CategoryHome.as_view(), name='category_home'),
    path('add/product/<slug:category>/', AddProduct.as_view(), name='add_product'),
    path('products/<slug:categort>/', ListProducts.as_view(), name='list_products'),
]