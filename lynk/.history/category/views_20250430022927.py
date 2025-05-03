from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from .models import Category, Product
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
class CategoryHome(View):
    def get(self, request):
        return render(request, 'category/category_home.html', {})

class AddProduct(LoginRequiredMixin, View):
    def get(self, request, category):
        if request.user.role != 'vendor':
            return redirect(reverse('home:home_page'))
        
        

