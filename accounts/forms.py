from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
# from .models import User
## Froms
User = get_user_model()

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
        fields = ('full_name', 'email', 'password', 'active', 'admin')


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
        if commit:
            user.save()
        return user






class GuestForm(forms.Form):
    email = forms.EmailField()


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email Address')
    password = forms.CharField(widget=forms.PasswordInput)




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
