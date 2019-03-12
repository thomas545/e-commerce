"""Accounts URL Configuration"""

from django.urls import path

from .views import guest_register_view, login_view, register_view
from django.contrib.auth.views import LoginView,LogoutView



app_name = "accounts"






urlpatterns = [
    path('guest-register/', guest_register_view, name='guest_register'),

    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    # path('register/', register, name='register'),
    # path('login/', LoginView.as_view(), name='login'),

    path('logout/', LogoutView.as_view(), name='logout'),
]
