from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
class CategoryHome(View):
    def get(self, request):
        return render(request, 'category/category_home.html', {})

class AddProduct(View):
    def get(self, request, category):
