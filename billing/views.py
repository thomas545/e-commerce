from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.utils.http import is_safe_url
# Create your views here.


import stripe
stripe.api_key = "sk_test_gnVSg3SSbYKxbTbPesQwsoTv"
STRIPE_PUB_KEY = 'pk_test_kC38CxS6Zu5j3HANr0FIkvgZ'

def payment_view(request):
    next_url = None
    next_ = request.GET.get('next')
    if is_safe_url(next_, request.get_host()):
        next_url = next_
    return render(request, 'payment/payment.html',{'publish_key':STRIPE_PUB_KEY, "next_url":next_url})



def payment_method_create_view(request):
    if request.method == 'POST' and request.is_ajax():
        print(request.POST)
        return JsonResponse({"message":"Success!, Your Card IS Added!"})
    return HttpResponse("Error", status_code=401)
