from django.shortcuts import render
from django.views import View
from category.models import Category, Product

# Create your views here.
class HomeView(View):
    def get(self, request):
        categories = Category.objects.all()
        products = Product.objects.all()
        ctx = {
            'categories': categories,
            'products': products,
        }
        return render(request, 'home/customer_home.html', {})