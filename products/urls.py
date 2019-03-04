"""products App URL Configuration"""
from django.urls import path
from products.views import ProductListView, ProductDetailView,ProductDetailSlugView



app_name = 'products'




urlpatterns = [

    path('', ProductListView.as_view(), name='list'),
    # path('<int:pk>/', ProductDetailView.as_view(), name='detail'),
    path('<slug:slug>/', ProductDetailSlugView.as_view(), name='detail'),
]
