from store.forms import LoginForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth import views as auth_views
# from .views import CustomPasswordResetView
# from .views import CustomPasswordResetConfirmView

app_name = 'store'


urlpatterns = [
    path('', views.home, name="home"),
    # URL for Cart and Checkout
    path('add-to-cart/', views.add_to_cart, name="add-to-cart"),
    path('remove-cart/<int:cart_id>/', views.remove_cart, name="remove-cart"),
    path('plus-cart/<int:cart_id>/', views.plus_cart, name="plus-cart"),
    path('minus-cart/<int:cart_id>/', views.minus_cart, name="minus-cart"),
    path('cart/', views.cart, name="cart"),
    path('checkout', views.checkout, name="checkout"),
    path('orders/', views.orders, name="orders"),
    path('about', views.about, name="about"),
    path('contact', views.contact, name="contact"),
    path('admin_index', views.admin_index, name="admin_index"),
    path('addBrand/', views.addBrand, name="addBrand"),
    path('editBrand/<str:id>', views.editBrand, name="editBrand"),
    path('deleteBrand/<str:id>', views.deleteBrand, name="deleteBrand"),

    path('addCategory/', views.addCategory, name="addCategory"),
    path('editCategory/<int:category_id>/', views.editCategory, name='editCategory'),
    path('deleteCategory/<int:id>/', views.deleteCategory, name='deleteCategory'),

    path('addProduct/', views.addProduct, name="addProduct"),
    path('editProduct/<int:product_id>/', views.editProduct, name='editProduct'),
    path('deleteProduct/<int:id>/', views.deleteProduct, name='deleteProduct'),

    path('addBaseType/', views.addBaseType, name="addBaseType"),
    path('deleteBaseType/<int:id>/', views.deleteBaseType, name='deleteBaseType'),

    #URL for Products
    path('product_detail/<str:id>/', views.product_detail, name="product_detail"),
    path('categories/', views.all_categories, name="all-categories"),
    path('category_products/<str:id>', views.category_products, name="category-products"),

    path('brand_products/<str:id>', views.brand_products, name="brand_products"),
    path('all_brands', views.all_brands, name="all_brands"),
    path('allCustomers', views.allCustomers, name="allCustomers"),
    path('allOrders', views.allOrders, name="allOrders"),
    path('editStatus/<str:id>', views.editStatus, name="editStatus"),
    path('checkoutPage', views.checkoutPage, name="checkoutPage"),

    path('shop/', views.shop, name="shop"),
    path('newArrivals/', views.newArrivals, name="newArrivals"),
    path('saleView/', views.saleView, name="saleView"),
    path('addReview/', views.addReview, name="addReview"),

    # URL for Authentication
    path('accounts/register/', views.RegistrationView.as_view(), name="register"),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='account/login.html', authentication_form=LoginForm), name="login"),
    path('accounts/profile/', views.profile, name="profile"),
    path('accounts/add-address/', views.AddressView.as_view(), name="add-address"),
    path('accounts/remove-address/<int:id>/', views.remove_address, name="remove-address"),
    path('accounts/logoutF/', views.logoutF, name="logoutF"),

    path('accounts/password-change/', auth_views.PasswordChangeView.as_view(template_name='account/password_change.html', form_class=PasswordChangeForm, success_url='/accounts/password-change-done/'), name="password-change"),
    path('accounts/password-change-done/', auth_views.PasswordChangeDoneView.as_view(template_name='account/password_change_done.html'), name="password-change-done"),

    path('accounts/password-reset/', auth_views.PasswordResetView.as_view(template_name='account/password_reset.html', form_class=PasswordResetForm, success_url='/accounts/password-reset/done/'), name="password-reset"), # Passing Success URL to Override default URL, also created password_reset_email.html due to error from our app_name in URL
    path('accounts/password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='account/password_reset_done.html'), name="password_reset_done"),
    path('accounts/password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='account/password_reset_confirm.html', form_class=SetPasswordForm, success_url='/accounts/password-reset-complete/'), name="password_reset_confirm"), # Passing Success URL to Override default URL
    path('accounts/password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='account/password_reset_complete.html'), name="password_reset_complete"),


    path('product/test/', views.test, name="test"),

    # urls for admin panel
    path('admin_login', views.admin_login, name='admin_login'),
    

    
]
