from django.urls import path
from .views import *

app_name = 'users'

urlpatterns = [
    path('', HomeUser.as_view(), name='home_users'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
]
