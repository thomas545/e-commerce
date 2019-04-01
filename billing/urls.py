""" billing URL Configuration """


from django.urls import path

from .views import payment_view, payment_method_create_view



app_name = "billing"


urlpatterns = [

    path('payment/', payment_view, name='payment'),
    path('create/payment/', payment_method_create_view, name='create-payment'),
]
