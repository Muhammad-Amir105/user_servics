from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (RegisterView, logoutView, ResetPasswordView, LoginginView, HomeView, list_category, create_category,
                    update_category, delete_category, list_products, create_product, delete_product_by_id, upload_product_images,
                    get_product_by_id, delete_product_image)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginginView.as_view(), name='login'),
    path('logout/', logoutView, name='logout'),
    path('home/', HomeView.as_view(), name='home'),
    path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='user_app/password_reset_complete.html'),
         name='password_reset_complete'),
    path('password-reset-confirm/<uidb64>/<token>/',
             auth_views.PasswordResetConfirmView.as_view(template_name='user_app/password_reset_confirm.html'),
             name='password_reset_confirm'),



    # this urls fetch the product management projects api-----------------------------
    #category api--------------------
    path('', list_category, name='list_category'),
    path('create_category/', create_category, name='create_category'),
    path('<int:category_id>/update_category/', update_category, name='update_category'),
    path('<int:category_id>/delete_category', delete_category, name='delete_category'),


    #product api --------------------
    path('list_products/', list_products, name='list_products'),
    path('<int:category_id>/create_product/', create_product, name='create_product'),
    path('<int:product_id>/delete_product/', delete_product_by_id, name='delete_product'),
    path('<int:product_id>/get_product_by_id/', get_product_by_id, name='get_product_by_id'),


    #image api--------------
    path('upload_images/<int:product_id>/', upload_product_images, name='upload_images'),
    path('delete_product_image/<int:image_id>/', delete_product_image, name='delete_product_image'),

]