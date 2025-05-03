from django.urls import path
from .views import *

app_name = 'delivery'

urlpatterns = [
    path('', DeliveryHome.as_view(), name='delivery_home'),
]