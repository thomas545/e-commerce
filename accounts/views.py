from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import RegisterForm, GuestForm, LoginForm, RegisterForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.utils.http import is_safe_url
from .models import GuestEmail
# Create your views here.
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


def login_view(request):
    form = LoginForm(request.POST or None)
    context = {
        "form":form
    }

    next_ = request.GET.get('next')
    next_post = request.POST.get('next')
    redirect_path = next_ or next_post or None
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            try:
                del request.session["guest_email_id"]
            except:
                pass 
            if is_safe_url(redirect_path, request.get_host()):
                return redirect(redirect_path)
            else:
                return redirect('/')
    return render(request, "registration/login.html", context)



User = get_user_model()
def register_view(request):
    form = RegisterForm(request.POST or None)
    context = {
        "form":form
    }
    if form.is_valid():
        # print(form.cleaned_data)
        username = form.cleaned_data.get("username")
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = User.objects.create_user(username, email, password)
        # print(user)
    return render(request, "registration/register.html", context)



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
