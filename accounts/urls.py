"""Accounts URL Configuration"""

from django.urls import path

from .views import register, guest_register_view
from django.contrib.auth.views import LoginView,LogoutView



app_name = "accounts"






urlpatterns = [
    path('guest-register/', guest_register_view, name='guest_register'),
    path('register/', register, name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
