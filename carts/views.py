from django.shortcuts import render, redirect
from .models import Cart
from accounts.forms import GuestForm, LoginForm
from addresses.forms import AddressForm
from addresses.models import Address
from accounts.models import GuestEmail
from billing.models import BillingProfile
from products.models import Product
from orders.models import Order

# Create your views here. Carts App

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

    login_form = LoginForm()
    gest_form = GuestForm()
    address_form = AddressForm()

    billing_address_id = request.session.get("billing_address_id", None)
    shipping_address_id = request.session.get("shipping_address_id", None)

    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)

    if billing_profile is not None:
        order_obj, order_obj_created = Order.objects.new_or_get(billing_profile, cart_obj)

   ######### adding addresses to order#########
        if shipping_address_id:
            order_obj.shipping_address = Address.objects.get(id=shipping_address_id)
            del request.session["shipping_address_id"]

        if billing_address_id:
            order_obj.billing_address = Address.objects.get(id=billing_address_id)
            del request.session["billing_address_id"]

        if billing_address_id or shipping_address_id:
            order_obj.save()

    context = {
        "order":order_obj ,
        "billing_profile":billing_profile,
        "guest_form":gest_form,
        "login_form":login_form,
        "address_form":address_form
    }


    return render(request, 'carts/checkout.html', context)
