from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from .models import Cart, CartProducts
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
class ViewCart(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != 'customer':
            return redirect(reverse('home:home_page'))
        
        user_cart, created = Cart.objects.get_or_create(user=request.user)
        cart_products = CartProducts.objects.filter(cart=user_cart)

        ctx = {
            'cart_products': cart_products
        }

        return render(request, 'cart/cart.html', ctx)
