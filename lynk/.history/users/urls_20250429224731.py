from django.urls import path
from .views import HomeUser

app_name = 'users'

urlpatterns = [
    path('', HomeUser.as_view(), name='home_users')
]
