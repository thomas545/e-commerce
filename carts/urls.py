"""Carts App URL Configuration"""
from django.urls import path
from .views import cart_home, cart_view



app_name = 'carts'




urlpatterns = [

    path('', cart_home, name='home'),
    path('view/', cart_view, name='view'),

]
