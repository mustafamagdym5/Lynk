from django.urls import path
from .views import *

app_name = 'category'

urlpatterns = [
    path('', CategoryHome.as_view(), name='category_home'),
    path('add/product/', AddProduct.as_view(), name='add_product'),
    path('products/list/<slug:category>/', ListProducts.as_view(), name='list_products'),
    path('view/product/<int:product_id>/', ViewProduct.as_view(), name='view_product'),
    path('update/product/<int:product_id>', UpdateProduct.as_view(), name='update_product'),
    path('delete/product/<int:product_id>', DeleteProduct.as_view(), name='delete_product'),
    path('search/', ProductSearchView.as_view(), name='search_results'),
]