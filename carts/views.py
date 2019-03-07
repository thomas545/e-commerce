from django.shortcuts import render, redirect
from .models import Cart
from products.models import Product
from orders.models import Order
# Create your views here.

# displaying cart contents
def cart_home(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)

    return render(request, 'carts/cart.html', {'cart':cart_obj})

# adding and revomeing cart contents
def cart_view(request):
    product_id = request.POST.get("product_id")
    if product_id is not None:
        try:
            product_obj = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            print("Product Is Gone?")
            return redirect("carts:home")
        cart_obj, new_obj = Cart.objects.new_or_get(request)
        if product_obj in cart_obj.products.all():
            cart_obj.products.remove(product_obj)
        else:
            cart_obj.products.add(product_obj)
        request.session['cart_item'] = cart_obj.products.count()
    return redirect("carts:home")

# CheckOut Porccess:
def check_home(request):
    cart_obj, cart_created = Cart.objects.new_or_get(request)
    order_obj = None
    if cart_created or cart_obj.products.count() == 0:
        return redirect("carts:home")
    else:
        order_obj, new_order = Order.objects.get_or_create(cart=cart_obj)

    return render(request, 'carts/checkout.html', {"order":order_obj})
