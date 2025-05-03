from django.shortcuts import render
from django.views import View
import stripe

# Create your views here.
class HomePayment(View):
    def get(self, request):
        return render(request, 'payment/payment_home.html', {})