from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from .models import Cart, CartProducts
from category.models import Product
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
class ViewCart(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != 'customer':
            return redirect(reverse('home:home_page'))
        
        user_cart, created = Cart.objects.get_or_create(user=request.user)
        cart_products = CartProducts.objects.filter(cart=user_cart)
        cost = 0
        for cart_product in cart_products:
            cost += cart_product.product.price

        ctx = {
            'cart_products': cart_products,
            'all_cost': cost,
        }

        return render(request, 'cart/cart.html', ctx)
    
class AddCart(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != 'customer':
            return redirect(reverse('home:home_page'))
        
        user_cart, created = Cart.objects.get_or_create(user=request.user)
        cart_products = CartProducts.objects.filter(cart=user_cart)

        ctx = {
            'cart_products': cart_products
        }

        return render(request, 'cart/cart.html', ctx)
    
    def post(self, request):
        if request.user.role != 'customer':
            return redirect(reverse('home:home_page'))

        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))

        product = get_object_or_404(Product, id=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartProducts.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        return redirect(reverse('cart:view_cart'))
    
class UpdateCartView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        quantity = int(request.POST.get('quantity', 1))
        cart = request.user.cart
        cart_item = get_object_or_404(CartProducts, cart=cart, product_id=product_id)

        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()

        return redirect(reverse('cart:view_cart'))
    

class DeleteCartItemView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        cart = request.user.cart
        cart_item = get_object_or_404(CartProducts, cart=cart, product_id=product_id)
        cart_item.delete()
        return redirect(reverse('cart:view_cart'))

