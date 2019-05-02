from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import RegisterForm, GuestForm, LoginForm, RegisterForm, ReactiveEmailForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.utils.http import is_safe_url
from .models import GuestEmail, EmailActivation
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, FormView, DetailView, View
from .signals import user_login_signals
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.safestring import mark_safe
from django.views.generic.edit import FormMixin

# Create your views here.

class AccountHomeView(LoginRequiredMixin, DetailView):
    template_name = 'accounts/home.html'

    def get_object(self):
        return self.request.user


# this method like LoginRequiredMixin
    # @method_decorator
    # def dispatch(self, request, *args, **kwargs):
    #     super(AccountHomeView, self).dispatch(request, *args, **kwargs)



class AccountEmailActivateView(FormMixin, View):
    success_url = '/accounts/login/'
    form_class = ReactiveEmailForm
    key = None

    def get(self, request, key=None, *args, **kwargs):
        self.key = key
        if key is not None:
            qs = EmailActivation.objects.filter(key__iexact=key)
            qs_confirmable = qs.confirm()
            if qs_confirmable.count() == 1:
                obj = qs_confirmable.first()
                obj.activate()
                messages.success(request, "Your email has been confirmed. Please Login!")
                return redirect("login")
            else:
                activate_qs = qs.filter(activated=True)
                if activate_qs.exists():
                    # reset_link = reverse("accounts:login")
                    msg = """ Your Email already confirmed. Please Login or click on forgot your password to reset your password""" # .format(link=reset_link)
                    messages.success(request, mark_safe(msg))
                    return redirect("login")
        context = {'form': self.get_form(), 'key':key}
        return render(request, 'registration/activation-error.html', context)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        msg = "Your activation link sent, Check your Email"
        messages.success(self.request, msg)
        email = form.cleaned_data.get("email")
        obj = EmailActivation.objects.email_exists(email).first()
        user = obj.user
        activation = EmailActivation.objects.create(user=user, email=email)
        activation.send_activation()
        return super(AccountEmailActivateView, self).form_valid(form)
    
    def form_invalid(self, form):
        context = {'form': form, 'key': self.key}
        return render(self.request, 'registration/activation-error.html', context)



def guest_register_view(request):
    form = GuestForm(request.POST or None)
    context = {
        "form":form
    }

    next_ = request.GET.get('next')
    next_post = request.POST.get('next')
    redirect_path = next_ or next_post or None
    if form.is_valid():
        email = form.cleaned_data.get('email')
        new_guest_email = GuestEmail.objects.create(email=email)
        request.session["guest_email_id"] = new_guest_email.id
        if is_safe_url(redirect_path, request.get_host()):
            return redirect(redirect_path)
        else:
            return redirect('/accounts/register/')
    return redirect('/cart/checkout/')



class LoginFormView(FormView):
    form_class = LoginForm
    template_name = 'register/login.html'
    success_url = '/'


    def form_valid(self, form):
        request = self.request
        next_ = request.GET.get('next')
        next_post = request.POST.get('next')
        redirect_path = next_ or next_post or None

        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            if not user.is_active:
                messages.error(request , "This User is Not Active")
                return super(LoginFormView, self).form_valid(form)
            login(request, user)
            user_login_signals.send(user.__class__, instance=user, request=request)
            try:
                del request.session["guest_email_id"]
            except:
                pass
            if is_safe_url(redirect_path, request.get_host()):
                return redirect(redirect_path)
            else:
                return redirect('/')

        return super(LoginFormView, self).form_valid(form)




## User regusterayion View
class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'register/register.html'
    success_url = reverse_lazy('accounts:login')





#
# User = get_user_model()
# def register_view(request):
#     form = RegisterForm(request.POST or None)
#     context = {
#         "form":form
#     }
#     if form.is_valid():
#         form.save()
#     return render(request, "registration/register.html", context)




# def login_view(request):
#     form = LoginForm(request.POST or None)
#     context = {
#         "form":form
#     }
#
#     next_ = request.GET.get('next')
#     next_post = request.POST.get('next')
#     redirect_path = next_ or next_post or None
#
#     if form.is_valid():
#         username = form.cleaned_data.get("username")
#         password = form.cleaned_data.get("password")
#         user = authenticate(request, username=email, password=password)
#         if user is not None:
#             login(request, user)
#             try:
#                 del request.session["guest_email_id"]
#             except:
#                 pass
#             if is_safe_url(redirect_path, request.get_host()):
#                 return redirect(redirect_path)
#             else:
#                 return redirect('/')
#     return render(request, "registration/login.html", context)




# ## not used
# def register(request):
#     if request.method == "POST":
#         form = RegisterForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get("username")
#             password = form.cleaned_data.get("password1")
#             messages.success(request ,'Your Account Has Been Created! You Can Login Now!')
#             return redirect('login')
#     else:
#         form = RegisterForm()
#
#     return render(request, "registration/register.html", {"form":form})
