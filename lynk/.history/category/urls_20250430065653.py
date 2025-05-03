from django.urls import path
from .views import *

app_name = 'category'

urlpatterns = [
    path('', CategoryHome.as_view(), name='category_home'),
    path('add/product/', AddProduct.as_view(), name='add_product'),
    path('products/list/<slug:category>/', ListProducts.as_view(), name='list_products'),
    path('view/product/<int:product_id>/', )
]