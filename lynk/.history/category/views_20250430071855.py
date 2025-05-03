from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from .models import Category, Product
from .forms import AddProductForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.text import slugify

# Create your views here.
class CategoryHome(View):
    def get(self, request):
        return render(request, 'category/category_home.html', {})

class AddProduct(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != 'vendor':
            return redirect(reverse('home:home_page'))
        form = AddProductForm()
        ctx = {
            'form': form,
        }
        return render(request, 'category/add_product.html', ctx)
    
    def post(self, request):
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.owner = request.user
            slug = slugify(form.cleaned_data['name'])
            product.slug = slug
            product.save()
            return redirect(reverse('home:home_page'))
        ctx = {
            'form': form,
        }
        return render(request, 'category/add_product.html', ctx)


class ListProducts(LoginRequiredMixin, View):
    def get(self, request, category):
        products = Product.objects.filter(category=category)
        ctx = {
            'products': products,
        }

        return render(request, 'category/products_list.html', ctx)
    

class ViewProduct(View):
    def get(self, request, product_id):
        product = Product.objects.get(id=product_id)
        ctx = {
            'product':product
        }
        return render(request, 'category/product_detail.html', ctx)
    

class UpdateProduct(View):
    def get(self, request, product_id):
        if request.user.role != 'vendor':
            return redirect(reverse('home:home_page'))
        product = Product.objects.get(id=product_id)
        form = AddProductForm(product)
        ctx = {
            'form': form,
        }
        return render(request, 'category/add_product.html', ctx)
    
    def post(self, request, product_id):
        old_product = get_object_or_404(Product, product_id)
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.owner = request.user
            slug = slugify(form.cleaned_data['name'])
            product.slug = slug
            product.save()
            return redirect(reverse('home:home_page'))
        ctx = {
            'form': form,
        }
        return render(request, 'category/add_product.html', ctx)

