from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, get_user_model
from django.core.exceptions import ValidationError
from .models import EmailActivation
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.http import is_safe_url
from django.contrib import messages
from .signals import user_login_signals
# from .models import User
## Froms
User = get_user_model()

class ReactiveEmailForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data.get("email")
        qs = EmailActivation.objects.email_exists(email)
        if not qs.exists():
            reg_link = reverse("accounts:register")
            msg = """This Email Does Not Exist , you should <a href="{link}">Register</a> ?!""".format(link=reg_link)
            raise forms.ValidationError(mark_safe(msg))
        return email



class UserAdminCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('full_name', 'email',)


    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Password Don't Match")

        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

# Change Admin form
class UserAdminChangeForm(forms.ModelForm):

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('full_name', 'email', 'password', 'is_active', 'admin')


    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]



# RegisterForm

class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('full_name', 'email',)


    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Password Don't Match")

        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = False          # for activain Email
        # obj, created = EmailActivation.objects.create(user=user)
        # obj.send_activation()  # i will use post_save
        if commit:
            user.save()
        return user


class GuestForm(forms.Form):
    email = forms.EmailField()


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email Address')
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        request = self.request
        data = self.cleaned_data
        email = data.get("email")
        password = data.get("password")
        user = authenticate(request, username=email, password=password)
        if user is None:
            raise ValidationError("Invalid Credentials")
        login(request, user)
        self.user = user
        user_login_signals.send(user.__class__, instance=user, request=request)
        try:
            del request.session["guest_email_id"]
        except:
            pass

        return data

    # def form_valid(self, form):
    #     request = self.request
    #     next_ = request.GET.get('next')
    #     next_post = request.POST.get('next')
    #     redirect_path = next_ or next_post or None
    #
    #
    #     if user is not None:
    #         if not user.is_active:
    #             messages.error(request , "This User is Not Active")
    #             return super(LoginFormView, self).form_valid(form)
    #
    #         user_login_signals.send(user.__class__, instance=user, request=request)
    #         try:
    #             del request.session["guest_email_id"]
    #         except:
    #             pass
    #         if is_safe_url(redirect_path, request.get_host()):
    #             return redirect(redirect_path)
    #         else:
    #             return redirect('/')
    #
    #     return super(LoginFormView, self).form_valid(form)


##################################################################################

# class RegisterForm(forms.Form):
#     username    = forms.CharField()
#     email       = forms.EmailField()
#     password    = forms.CharField(widget=forms.PasswordInput)
#     password2   = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)
#
#     def clean_username(self):
#         username = self.cleaned_data.get("username")
#         qs = User.objects.filter(username=username)
#         if qs.exists():
#             raise forms.ValidationError("Username Is Taken.")
#             return username
#
#     def clean_email(self):
#         email = self.cleaned_data.get("email")
#         qs = User.objects.filter(email=email)
#         if qs.exists():
#             raise forms.ValidationError("E-mail Is Taken.")
#             return email
#
#     def clean(self):
#         data = self.cleaned_data
#         password = self.cleaned_data.get("password")
#         password2 = self.cleaned_data.get("password2")
#         if password != password2:
#             raise forms.ValidationError("Password Don't Match")
#         return data
#

# def form_valid(self, form):
#         request = self.request
#         next_ = request.GET.get('next')
#         next_post = request.POST.get('next')
#         redirect_path = next_ or next_post or None

#         email = form.cleaned_data.get("email")
#         password = form.cleaned_data.get("password")
#         user = authenticate(request, username=email, password=password)
#         if user is not None:
#             if not user.is_active:
#                 messages.error(request , "This User is Not Active")
#                 return super(LoginFormView, self).form_valid(form)
#             login(request, user)
#             user_login_signals.send(user.__class__, instance=user, request=request)
#             try:
#                 del request.session["guest_email_id"]
#             except:
#                 pass
#             if is_safe_url(redirect_path, request.get_host()):
#                 return redirect(redirect_path)
#             else:
#                 return redirect('/')

#         return super(LoginFormView, self).form_valid(form)

## not used yet
# class RegisterForm(UserCreationForm):
#     class Meta:
#         model = User
#         fields = ["username", "email"]
#
#     def __init__(self, *args, **kwargs):
#         super(RegisterForm, self).__init__(*args, **kwargs)
#
#         for fieldname in ["username", "password1", "password2"]:
#             self.fields[fieldname].help_text = None
