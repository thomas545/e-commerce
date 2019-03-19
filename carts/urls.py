"""Carts App URL Configuration"""
from django.urls import path
from .views import cart_home, cart_view, check_home, check_done_view,cart_detail_api_view



app_name = 'carts'    # /cart/




urlpatterns = [

    path('', cart_home, name='home'),
    path('view/', cart_view, name='view'),
    path('checkout/', check_home, name='checkout'),
    path('success/', check_done_view, name='success'),
    path('api/cart/', cart_detail_api_view, name='cart_api'),


]
