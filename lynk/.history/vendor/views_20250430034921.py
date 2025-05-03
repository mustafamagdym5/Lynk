from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
class VendorHome(View):
    def get(self, request):
        return(request, 'vendor/venfor_home.html')