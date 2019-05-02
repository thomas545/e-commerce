"""Accounts URL Configuration"""

from django.urls import path, re_path
from django.views.generic import RedirectView
from .views import guest_register_view, LoginFormView, RegisterView, AccountHomeView, AccountEmailActivateView
from django.contrib.auth.views import LoginView,LogoutView



app_name = "accounts"




urlpatterns = [
    path('guest-register/', guest_register_view, name='guest_register'),
    path('', AccountHomeView.as_view(), name='home'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginFormView.as_view(), name='login'),
    # path('register/', register, name='register'),
    # re_path('email/confirm/(?P<key>[0-9A-Za-z]+)/', AccountEmailActivateView.as_view(), name='activate'),
    path('email/confirm/<str:key>/', AccountEmailActivateView.as_view(), name='activate'),
    path('email/resend-activation/', AccountEmailActivateView.as_view(), name='resend'),
    path('logout/', LogoutView.as_view(), name='logout'),

]
