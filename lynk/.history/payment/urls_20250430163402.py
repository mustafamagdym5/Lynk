from django.urls import path
from .views import *

app_name = 'payment'

urlpatterns = [
    path('', HomePayment.as_view(), name='home_payment'),
    path('check-out/', ProductView.as_view(), name='check_out'),
    path('payment_successful/', PaymentSuccessful.as_view(), name='payment_successful'),
    path('payment_cancelled/', PaymentCancelled.as_view(), name='payment_cancelled'),
]