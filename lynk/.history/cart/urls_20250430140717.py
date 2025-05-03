from django.urls import path
from .views import *

app_name = 'cart'

urlpatterns = [
    path('view/cart/', ViewCart.as_view(), name='view_cart'),
    path('add/cart/', AddCart.as_view(), name='add_cart'),
    path('update/<int:product_id>/', UpdateCartView.as_view(), name='update_cart'),
]