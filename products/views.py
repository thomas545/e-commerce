from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.views.generic import ListView,DetailView,CreateView,UpdateView,DeleteView
from .models import Product
from carts.models import Cart
# Create your views here.


class ProductListView(ListView):
    model = Product
    template_name = "products/list.html"



class ProductDetailSlugView(DetailView):
    model = Product
    template_name = "products/detail.html"


    ## put cart in detail page
    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailSlugView, self).get_context_data(*args,**kwargs)
        cart_obj, new_obj = Cart.objects.new_or_get(self.request)
        context["cart"] = cart_obj
        return context

    ## handeling error MultipleObjectsReturned ##
    def get_object(self,*args,**kwargs):
        request = self.request
        slug = self.kwargs.get('slug')
        # instance = get_object_or_404(Product, slug=slug, active=True)
        try:
            instance = Product.objects.get(slug=slug, active=True)
        except Product.DoesNotExist:
            raise Http404("Not Found....")
        except Product.MultipleObjectsReturned :
            qs = Product.objects.filter(slug=slug, active=True)
            instance = qs.first()
        except :
            raise Http404("Ohh.. Error")
        return instance




# Not important
class ProductDetailView(DetailView):
    model = Product
    template_name = "products/detail.html"
