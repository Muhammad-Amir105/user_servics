from django.contrib import messages

# from django.contrib.auth.models import User
from django import forms
from django.db.transaction import commit
from .models import CustomUser


class RegistrationForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=[('customer', 'Customer'), ('vendor', 'Vendor')], required=True)


    def clean_username(self):
        username = self.cleaned_data['username']
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password != password2:
            raise forms.ValidationError("Passwords don't match")

        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long")
        return cleaned_data


    def save(self):
        user = CustomUser(username=self.cleaned_data['username'], email=self.cleaned_data['email'])
        user.set_password(self.cleaned_data['password'])

        role = self.cleaned_data['role']
        if role == 'vendor':
            user.role = 'customer'
            user.pending_vendor = True
        else:
            user.role = 'customer'

        if commit:
            user.save()
        return user



class CreateCategoryForm(forms.Form):
    name = forms.CharField()
    description = forms.CharField()

class updateCategoryForm(forms.Form):
    name = forms.CharField(required=False)
    description = forms.CharField(required=False)


class AddProductForm(forms.Form):
    name = forms.CharField()
    description = forms.CharField()
    price = forms.DecimalField()
    stock = forms.IntegerField()

class UpdateProductForm(forms.Form):
    name = forms.CharField(required=False)
    description = forms.CharField(required=False)
    price = forms.DecimalField(required=False)
    stock = forms.IntegerField(required=False)


