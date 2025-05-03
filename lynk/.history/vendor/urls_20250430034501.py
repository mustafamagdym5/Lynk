from django.urls import path
from .views import *

app_name = 'vendor'

urlpatterns = [
    path('', v)
]