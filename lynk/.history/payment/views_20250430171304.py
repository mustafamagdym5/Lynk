from django.shortcuts import render,redirect
from django.urls import reverse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
import stripe
from django.conf import settings
from cart.models import Cart, CartProducts
from .models import UserPayment, StripeProduct

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
class HomePayment(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'payment/payment_home.html', {})
    
class ProductView(LoginRequiredMixin, View):
    def get(self, request):
        try:
            # Get the user's cart
            cart = Cart.objects.get(user=request.user)
            cart_products = CartProducts.objects.filter(cart=cart)
            
            # Prepare line items for Stripe
            line_items = []
            for item in cart_products:
                # Get or create Stripe product for each item
                stripe_product, created = StripeProduct.objects.get_or_create(
                    item=item.product,
                    defaults={
                        'stripe_product_id': 'will_be_set_in_post',
                        'stripe_price_id': 'will_be_set_in_post'
                    }
                )
                
                if created or not stripe_product.stripe_product_id:
                    # Create product in Stripe if it doesn't exist
                    product = stripe.Product.create(
                        name=item.item.name,
                        description=item.item.description[:500] if item.item.description else "",
                        images=[item.item.image.url] if item.item.image else []
                    )
                    
                    # Create price in Stripe
                    price = stripe.Price.create(
                        product=product.id,
                        unit_amount=int(item.item.get_discounted_price() * 100),  # Convert to cents
                        currency='egp',
                    )
                    
                    # Update our StripeProduct model
                    stripe_product.stripe_product_id = product.id
                    stripe_product.stripe_price_id = price.id
                    stripe_product.save()
                
                line_items.append({
                    'price': stripe_product.stripe_price_id,
                    'quantity': item.quantity,
                })
            
            ctx = {
                'cart_items': cart_products,
                'total': sum(item.total_price for item in cart_products),
            }
            return render(request, 'payment/check_out.html', ctx)
        
        except Cart.DoesNotExist:
            return redirect(reverse('cart:view_cart'))
    
    def post(self, request):
        if request.user.role != 'customer':
            return redirect(reverse('home:home_page'))
        
        try:
            cart = Cart.objects.get(user=request.user)
            cart_products = CartProducts.objects.filter(cart=cart)
            
            if not cart_products.exists():
                return redirect(reverse('cart:view_cart'))
            
            # Prepare line items for Stripe checkout
            line_items = []
            for item in cart_products:
                stripe_product = StripeProduct.objects.get(item=item.item)
                line_items.append({
                    'price': stripe_product.stripe_price_id,
                    'quantity': item.quantity,
                })
            
            checkout_session = stripe.checkout.Session.create(
                line_items=line_items,
                payment_method_types=['card'],
                mode='payment',
                customer_creation='always',
                success_url=f'{settings.BASE_URL}{reverse("payment:payment_successful")}?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=f'{settings.BASE_URL}{reverse("payment:payment_cancelled")}',
            )
            return redirect(checkout_session.url, code=303)
        
        except Cart.DoesNotExist:
            return redirect(reverse('cart:view_cart'))


class PaymentSuccessful(View):
    def get(self, request):
        user_cart = Cart.objects.get(user=request.user)
        cart_products = CartProducts.objects.filter(cart=user_cart)
        cart_products.delete()
        
        checkout_session_id = request.GET.get('session_id', None)
        if checkout_session_id:
            session = stripe.checkout.Session.retrieve(checkout_session_id)
            customer_id = session.customer
            customer = stripe.Customer.retrieve(customer_id)
        
        line_item = stripe.checkout.Session.list_line_items(checkout_session_id).data[0]
        UserPayment.objects.get_or_create(
            user = request.user, 
            stripe_customer_id = customer_id,
            stripe_checkout_id = checkout_session_id,
            stripe_product_id = line_item.price.product,
            product_name = line_item.description,
            quantity = line_item.quantity,
            price = line_item.price.unit_amount / 100.0,
            currency = line_item.price.currency,
            has_paid = True
        )
        ctx = {
            'customer': customer,
        }
        return render(request, 'payment/payment_successful.html', ctx)
    

class PaymentCancelled(View):
    def get(self, request):
        return render(request, 'payment/payment_cancelled.html')