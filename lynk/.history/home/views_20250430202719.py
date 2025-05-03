from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from category.models import Category, Product

# Create your views here.
class HomeView(View):
    def get(self, request):
        if request.user.is_authenticated and request.user.role == 'vendor':
            return redirect(reverse('vendor:vendor_home'))
        if request.user.is_authenticated and request.user.role == 'delivey':
            return redirect(reverse('delivery:vendor_delivery'))
        categories = Category.objects.all()
        products = Product.objects.all()
        ctx = {
            'categories': categories,
            'products': products,
        }
        if request.user.is_authenticated:
            print(request.user.latitude, request.user.longitude)
        return render(request, 'home/customer_home.html', ctx)