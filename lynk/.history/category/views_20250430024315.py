from django.shortcuts import render, redirect
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
            product.category = Category.objects.get(slug=category)
