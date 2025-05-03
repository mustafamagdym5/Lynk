from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from category.models import Category, Product

# Create your views here.
class HomeView(View):
    def get(self, request):
        if request.user.is_authenticated and request.user.role == 'vendor':
            return redirect(reverse('vendor:home_vendor'))
        categories = Category.objects.all()
        products = Product.objects.all()
        ctx = {
            'categories': categories,
            'products': products,
        }
        return render(request, 'home/customer_home.html', ctx)