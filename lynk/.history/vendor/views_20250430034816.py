from django.shortcuts import render
from django.views import View

# Create your views here.
class VendorHome(View):
    def get(self, request):
        return(request, 'vendor/venfor_home.html')