from django.shortcuts import render, redirect
from .models import Cart
from django.http import JsonResponse
from accounts.forms import GuestForm, LoginForm
from addresses.forms import AddressForm
from addresses.models import Address
from accounts.models import GuestEmail
from billing.models import BillingProfile
from products.models import Product
from orders.models import Order

# Create your views here. Carts App


def cart_detail_api_view(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)

    products = [{
                "id": x.id,
                "url": x.get_absolute_url(),
                "name": x.title,
                 "price": x.price
                 }
            for x in cart_obj.products.all()]

    cart_data = {"products":products, "subtotal":cart_obj.subtotal, "total":cart_obj.total}

    return JsonResponse(cart_data)




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
            added = False
        else:
            cart_obj.products.add(product_obj)
            added = True
        request.session['cart_item'] = cart_obj.products.count()
        if request.is_ajax(): # for Ajax request to handel add and remove
            json_data = {
                "added":added,
                "remove": not added,
                "cartCount": cart_obj.products.count()
            }
            return JsonResponse(json_data)
            # return JsonResponse({"message":"Error 400"}, status_code=400) testing jquery
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
    address_qs = None
    if billing_profile is not None:
        if request.user.is_authenticated:
            address_qs = Address.objects.filter(billing_profile=billing_profile)
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


    if request.method == 'POST':
        is_done = order_obj.check_done()
        if is_done:
            order_obj.mark_paid()
            request.session['cart_item'] = 0
            del request.session['cart_id']
            return redirect('carts:success')


    context = {
        "order":order_obj ,
        "billing_profile":billing_profile,
        "guest_form":gest_form,
        "login_form":login_form,
        "address_form":address_form,
        "address_qs":address_qs
    }


    return render(request, 'carts/checkout.html', context)



# displaying Sucsess Page
def check_done_view(request):

    return render(request, 'carts/success.html', {})
