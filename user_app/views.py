from http.client import responses

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordResetView, LoginView
from django.contrib.messages.views import SuccessMessageMixin
# from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView
from django.conf import settings
import user_app
from .decorators import role_required
from .forms import RegistrationForm, CreateCategoryForm, updateCategoryForm, AddProductForm
from .models import CustomUser


class RegisterView(FormView):
    model = CustomUser
    form_class = RegistrationForm
    template_name = 'user_app/register.html'
    # success_url = reverse_lazy('login')

    def get_success_url(self):
        return reverse_lazy('login')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        username = form.cleaned_data['username']
        role = form.cleaned_data['role']

        form.save()

        if role == 'vendor':
            send_email_admin(email, username)
        else:
            send_email_user(email)
        messages.success(self.request, 'Registration Successful')
        return super().form_valid(form)



class LoginginView(LoginView):
    template_name = 'user_app/login.html'
    # redirect_authenticated_user = True
    next_page = 'list_category'

    def form_valid(self, form):
        messages.success(self.request, 'You are now logged in.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password, please try again.')
        return self.render_to_response(self.get_context_data(form=form))

# def loginView(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             return redirect('home')
#         else:
#             return render(request, 'user_app/login.html', {'error':'invalid username or password'})
#
#     else:
#         return render(request, 'user_app/login.html')



class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'user_app/password_reset.html'
    email_template_name = 'user_app/password_reset_email.html'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('login')

    def get_subject(self):
        return 'Django - Registration/Login App Password Reset'

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'user_app/home.html'
    login_url = 'login'


# @login_required(login_url='login')
# def home(request):
#     return render(request, 'user_app/home.html')


def logoutView(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')


def send_email_user(email):
    subject = 'confirm your email'
    message = 'welcome to the website name!!'
    from_email = settings.EMAIL_HOST_USER
    to_list = [email]
    send_mail(subject, message, from_email, to_list, fail_silently=True)


def send_email_admin(email, username):
    subject = 'Approve the role'
    message = f'Hy this is {username} please approve my role'
    from_email = settings.EMAIL_HOST_USER
    to_list = ['pythonmafia1@gmail.com']
    send_mail(subject, message, from_email, to_list, fail_silently=True)



#category view-----------------
import requests
from django.http import JsonResponse
fastapi_url = 'http://0.0.0.0:8080/'


@role_required('customer', 'vendor')
def list_category(request):
    try:
        response = requests.get(f"{fastapi_url}/categories/", verify=False)
        if response.status_code == 200:
            categories = response.json()
        else:
            categories = []
        return render(request, 'user_app/home_dir/home.html', {'categories': categories, 'user': request.user})
    except:
        return render(request, 'user_app/home_dir/home.html', {'categories': [], 'user': request.user})

@role_required('vendor')
def create_category(request):
    if request.method == "POST":
        form = CreateCategoryForm(request.POST)
        if form.is_valid():
            data = {
                "name": form.cleaned_data['name'],
                "description": form.cleaned_data['description'],
            }
            headers = {
                "Content-Type": "application/json"
            }
            response = requests.post(f"{fastapi_url}/categories", json=data, headers=headers, verify=False)
            create_response = response.json().get("message", "Category created successfully")
            messages.success(request, create_response)
            return redirect('list_category')
        else:
            return JsonResponse({"error": "Invalid form data"}, status=400)

    # GET request par HTML form return karo
    form = CreateCategoryForm()
    return render(request, "user_app/create_category.html", {"form": form})

@role_required('vendor')
def update_category(request, category_id):
    response = requests.get(f"{fastapi_url}/category/{category_id}/", verify=False)
    if response.status_code == 200:
        category_data = response.json()
    else:
        messages.error(request, "Failed to fetch category details")
        return redirect('list_category')

    if request.method == "POST":
        form = updateCategoryForm(request.POST)
        if form.is_valid():
            data = {
                'name': form.cleaned_data['name'],
                'description': form.cleaned_data['description'],
            }
            headers = {
                "Content-Type": "application/json"
            }
            response = requests.put(f"{fastapi_url}/categories/{category_id}", json=data, headers=headers, verify=False)
            update_response = response.json().get("message", "Category update successfully")
            messages.success(request, update_response)
            return redirect('list_category')
        else:
            return JsonResponse({"error": "Invalid form data"}, status=400)

    else:
        form = updateCategoryForm(initial={
            'name': category_data.get('name', ''),
            'description': category_data.get('description', ''),
        })
    return render(request, "user_app/create_category.html", {"form": form})

@role_required('vendor')
def delete_category(request, category_id):
    response = requests.delete(f"{fastapi_url}/categories/{category_id}", verify=False)
    deleted_response = response.json()
    if response.status_code == 200:
        messages.success(request, deleted_response)
        return redirect('list_category')
    else:
        return redirect('list_category')


#product view---------------------------------

@role_required('vendor', 'customer')
def list_products(request):
    response = requests.get(f"{fastapi_url}/products/", verify=False)
    if response.status_code == 200:
        products = response.json()
        messages.success(request, products)
        return render(request, 'user_app/home_dir/product_home.html', {'products': products, 'user': request.user})
    else:
        return render(request, 'user_app/home_dir/product_home.html', {'products': [], 'user': request.user})

@role_required('vendor')
def create_product(request, category_id):
    if request.method == "POST":
        form = AddProductForm(request.POST)
        if form.is_valid():
            data = {
                'name': form.cleaned_data['name'],
                'description': form.cleaned_data['description'],
                'price': float(form.cleaned_data['price']),
                'stock': form.cleaned_data['stock'],
                'category_id': category_id,
            }
            headers = {
                "Content-Type": "application/json"
            }
            response = requests.post(f"{fastapi_url}/product", json=data, headers=headers, verify=False)
            create_response = response.json().get("message", "Product created successfully")
            messages.success(request, create_response)
            return redirect('list_products')
        else:
            return JsonResponse({"error": "Invalid form data"}, status=400)

    form = AddProductForm()
    return render(request, 'user_app/home_dir/create_product.html', {'form': form})


@role_required('vendor')
def delete_product_by_id(request, product_id):
    response = requests.delete(f"{fastapi_url}/product/{product_id}", verify=False)
    if response.status_code == 200:
        messages.success(request, "Product deleted successfully")
        return redirect('list_products')
    else:
        messages.error(request, "Failed to fetch product details")
        return redirect('list_products')


def get_product_by_id(request, product_id):
    response = requests.get(f"{fastapi_url}/product/{product_id}/", verify=False)
    if response.status_code == 200:
        product_data = response.json()
        messages.success(request, product_data)
        return redirect('list_products')
    else:
        messages.error(request, "Failed to fetch product details")
        return redirect('list_products')


#product images view---------------------

@role_required('vendor')
def upload_product_images(request, product_id):
    if request.method == "POST" and request.FILES:
        files = request.FILES.getlist('images')
        upload_files = [('images', (f.name, f.read(), f.content_type)) for f in files]

        response = requests.post(f"{fastapi_url}/product_images/{product_id}", files=upload_files)

        if response.status_code == 200:
            return redirect('list_products')
        else:
            return render(request, "user_app/home_dir/product_image_upload.html", {"error": "Upload Failed!"})

    return render(request, "user_app/home_dir/product_image_upload.html")

@role_required('vendor')
def delete_product_image(request, image_id):
    response = requests.delete(f"{fastapi_url}/delete_product_image_by_image_id/{image_id}", verify=False)
    if response.status_code == 200:
        return redirect('list_products')




