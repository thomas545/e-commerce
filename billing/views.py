from django.shortcuts import render

# Create your views here.


import stripe
stripe.api_key = "sk_test_gnVSg3SSbYKxbTbPesQwsoTv"
STRIPE_PUB_KEY = 'pk_test_kC38CxS6Zu5j3HANr0FIkvgZ'

def payment_method(request):
    if request.method == 'POST':
        print(request.POST)

    return render(request, 'payment/payment.html',{'publish_key':STRIPE_PUB_KEY})
