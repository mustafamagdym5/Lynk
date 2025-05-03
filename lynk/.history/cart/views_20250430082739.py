from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from .models import Cart, CartProducts
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
class ViewCart(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != 'customer':
            return redirect(reverse('home:home_page'))
        
        user_cart = Cart.objects.filter(user=request.user)