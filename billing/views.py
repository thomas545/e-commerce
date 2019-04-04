from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.utils.http import is_safe_url
from .models import BillingProfile, Card
# Create your views here.


import stripe
stripe.api_key = "sk_test_gnVSg3SSbYKxbTbPesQwsoTv"
STRIPE_PUB_KEY = 'pk_test_kC38CxS6Zu5j3HANr0FIkvgZ'

def payment_view(request):

    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
    if not billing_profile:
        return redirect("/cart")
    next_url = None
    next_ = request.GET.get('next')
    if is_safe_url(next_, request.get_host()):
        next_url = next_
    return render(request, 'payment/payment.html',{'publish_key':STRIPE_PUB_KEY, "next_url":next_url})



def payment_method_create_view(request):
    if request.method == 'POST' and request.is_ajax():
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
        if not billing_profile:
            return HttpResponse({"message":"This User Not Found!"}, status_code=401)

        token = request.POST.get("token")
        if token is not None:
            # card = stripe.Customer.create_source(billing_profile.customer_id,source=token)
            # new_card_obj = Card.objects.add_new(billing_profile, card)
            new_card_obj = Card.objects.add_new(billing_profile, token)
        return JsonResponse({"message":"Success!, Your Card IS Added!"})
    return HttpResponse("Error", status_code=401)
