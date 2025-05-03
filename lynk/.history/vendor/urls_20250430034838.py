from django.urls import path
from .views import *

app_name = 'vendor'

urlpatterns = [
    path('', VendorHome.as_view(), name='vendor_home'),
]