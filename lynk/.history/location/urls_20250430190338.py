from django.urls import path
from .views import *

app_name = 'location'

urlpatterns = [
    path('', HomeLocation.as_view(), name='home_location'),
    path('choose/location', ChooseFromMap.as_view(), name='choose_location'),
]