from .models import CartProducts

def cart_quantity(request):
    quantity = 0
    if request.user.is_authenticated and hasattr(request.user, 'cart'):
        quantity = sum(item.quantity for item in CartProducts.objects.filter(cart=request.user.cart))
    return {'cart_quantity': quantity}
