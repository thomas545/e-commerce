""" billing URL Configuration """


from django.urls import path

from .views import payment_method



app_name = "billing"


urlpatterns = [

    path('payment/', payment_method, name='payment'),
]
