from django.urls import path
from .views import *

app_name = 'payment'

urlpatterns = [
    path('', HomePayment.as_view(), name='home_payment'),
    path('check-out/', CheckOutView.as_view(), name='check_out'),
    path('payment_successful/', PaymentSuccessful.as_view(), name='payment_successful'),
    path('payment_cancelled/', PaymentCancelled.as_view(), name='payment_cancelled'),
    path('delivery_payment_success/', DeliveryPaymentSuccessful.as_view(), name='delivery_payment_success'),
path('delivery_payment_cancelled/', DeliveryPaymentCancelled.as_view(), name='delivery_payment_cancelled'),
]