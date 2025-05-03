from django.urls import path
from .views import *

app_name = 'category'

urlpatterns = [
    path('', CategoryHome.as_view(), name='category_home'),
    path('add/item/<slug:category>')
]