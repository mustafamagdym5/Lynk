from django.urls import path
from .views import *

app_name = 'users'

urlpatterns = [
    path('', HomeUser.as_view(), name='home_users'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterHome.as_view(), name='register'),
    path('register_customer/', RegisterCustomer.as_view(), name='register_customer'),
    path('register_vendor/', RegisterVendor.as_view(), name='register_vendor'),
    path('register_delivery/', RegisterDelivery.as_view(), name='register_delivery'),
]
