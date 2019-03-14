from django.urls import path

from .views import checkout_address_create_view




app_name = "address"



urlpatterns = [
    path('checkout/address/create/', checkout_address_create_view, name='checkout_address_create'),

]
