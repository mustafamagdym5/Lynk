from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from .models import Category, Product
from .forms import AddProductForm
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
class CategoryHome(View):
    def get(self, request):
        return render(request, 'category/category_home.html', {})

class AddProduct(LoginRequiredMixin, View):
    def get(self, request, category):
        if request.user.role != 'vendor':
            return redirect(reverse('home:home_page'))
        form = AddProductForm()
        ctx = {
            'form': form,
        }
        return render(request, 'category/add_product.html', ctx)
    
    def post(self, request, category):
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.owner = request.user
            product.category = get_object_or_404(Category, slug=category)
            return redirect(reverse('home:home_page'))
        ctx = {
            'form': form,
        }
        return render(request, 'category/add_product.html', ctx)


class ListProducts(LoginRequiredMixin, View):
    def get(self, request, category):
        products = Product.objects.get(slug=category)
        ctx = {
            'products': products,
        }

        return render(request, 'category/products_list')