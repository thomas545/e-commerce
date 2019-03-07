from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import RegisterForm
from django.contrib import messages
# Create your views here.


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")
            messages.success(request ,'Your Account Has Been Created! You Can Login Now!')
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, "registration/register.html", {"form":form})
