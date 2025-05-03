from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from category.models import Category, Product

# Create your views here.
class VendorHome(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != 'vendor':
            return redirect(reverse('home:home_page'))
        
        products = Product.objects.filter(owner=request.user)
        ctx = {
            'products': products
        }
        return render(request, 'vendor/vendor_home.html', ctx)