""" ecommerce URL Configuration """


from django.contrib import admin
from django.urls import path, include

from .views import HomeView
from django.views.generic import RedirectView

from django.conf import settings
from django.conf.urls.static import static
# from carts.views import cart_detail_api_view
################ admin pgae customize #####################

admin.site.site_header = 'Ecommerce admin'
admin.site.site_title = 'Ecommerce admin'
# admin.site.site_url = 'http://coffeehouse.com/'
admin.site.index_title = 'Ecommerce administration'
# admin.empty_value_display = '**Empty**'
###########################################################



urlpatterns = [
    path('admin/', admin.site.urls),
    path('settings/', RedirectView.as_view(url='/accounts')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('account/', include('accounts.password.urls', namespace='account')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('products/', include('products.urls', namespace='products')),
    path('marketing/', include('marketing.urls', namespace='marketing')),
    path('address/', include('addresses.urls', namespace='address')),
    path('billing/', include('billing.urls', namespace='billing')),
    # path('api/cart/', cart_detail_api_view, name='cart_api'),
    path('cart/', include('carts.urls', namespace='carts')),
    path('search/', include('search.urls', namespace='search')),
    path('', HomeView.as_view(), name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
