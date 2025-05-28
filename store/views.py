import django
from django.contrib.auth.models import User
from store.models import Address, Cart, Category, Order, Product
from django.shortcuts import redirect, render, get_object_or_404
from .forms import RegistrationForm, AddressForm
from django.contrib import messages
from django.views import View
import decimal
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator # for Class Based Views
from django.contrib import messages
from .models import *
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from datetime import date
from django.core.paginator import Paginator
from django.db.models import Sum
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetDoneView
from django.urls import reverse_lazy

# Create your views here.

# class CustomPasswordResetConfirmView(PasswordResetConfirmView):
#     success_url = reverse_lazy('store:login')  

#     def get_success_url(self):
#         return self.success_url

#     def form_invalid(self, form):
#         return self.render_to_response(self.get_context_data(form=form))


# class CustomPasswordResetDoneView(PasswordResetDoneView):
#     success_url = reverse_lazy('password_reset_done')  

#     def get_success_url(self):
#         return self.success_url


# def password_reset_done(request):
#     return render(request, 'account/password_reset_done.html')


# class CustomPasswordResetView(PasswordResetView):
#     template_name = 'account/password_reset.html'
#     email_template_name = 'account/password_reset_email.html'
#     success_url = reverse_lazy('password_reset_done')
#     form_class = PasswordResetForm


def about(request):
    return render(request,'about.html')

def contact(request):
    return render(request,'contact.html')


def home(request):
    categories = Category.objects.filter(is_active=True, is_featured=True)
    brands = Brand.objects.all()[:9]

    products_paginator = Product.objects.filter(is_active=True, is_featured=True) 
    paginator = Paginator(products_paginator, 100) 
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
  
    context = {
        'categories': categories,
        'products': products,
        'brands':brands,
        
    }
    return render(request, 'store/index.html', context)


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    related_products = Product.objects.exclude(id=product.id).filter(is_active=True, category=product.category)
    context = {
        'product': product,
        'related_products': related_products,

    }
    return render(request, 'store/detail.html', context)


def all_categories(request):
    categories = Category.objects.filter(is_active=True)
    return render(request, 'store/categories.html', {'categories':categories})


def category_products(request, id):
    category = get_object_or_404(Category, id=id)
    categories = Category.objects.filter(is_active=True)

    products_paginator = Product.objects.filter(is_active=True, category=category) 
    paginator = Paginator(products_paginator, 100) 
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'products': products,
        'categories': categories,
    }
    return render(request, 'store/category_products.html', context)

def brand_products(request, id):
    brand = get_object_or_404(Brand, id=id)
    brands = Brand.objects.all()

    products_paginator = Product.objects.filter(is_active=True, category__brand=brand) 
    paginator = Paginator(products_paginator, 100) 
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    context = {
        'brand': brand,
        'products': products,
        'brands': brands,
    }
    return render(request, 'store/brand_products.html', context)


def all_brands(request):
   
    brands = Brand.objects.all()

    context = {
        'brands': brands,
    }

    return render(request, 'store/all_brands.html', context)

# Authentication Starts Here

class RegistrationView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'account/register.html', {'form': form})
    
    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, "Congratulations! Registration Successful!")
            form.save()
        return render(request, 'account/register.html', {'form': form})
        

@login_required
def profile(request):
    addresses = Address.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user)
    return render(request, 'account/profile.html', {'addresses':addresses, 'orders':orders})


@method_decorator(login_required, name='dispatch')
class AddressView(View):
    def get(self, request):
        form = AddressForm()
        return render(request, 'account/add_address.html', {'form': form})

    def post(self, request):
        form = AddressForm(request.POST)
        if form.is_valid():
            user=request.user
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            reg = Address(user=user, locality=locality, city=city, state=state)
            reg.save()
            messages.success(request, "New Address Added Successfully.")
        return redirect('store:profile')


@login_required
def remove_address(request, id):
    a = get_object_or_404(Address, user=request.user, id=id)
    a.delete()
    messages.success(request, "Address removed.")
    return redirect('store:profile')

@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = get_object_or_404(Product, id=product_id)

    # Check whether the Product is alread in Cart or Not
    item_already_in_cart = Cart.objects.filter(product=product_id, user=user)
    if item_already_in_cart:
        cp = get_object_or_404(Cart, product=product_id, user=user)
        cp.quantity += 1
        cp.save()
    else:
        Cart(user=user, product=product).save()
    
    return redirect('store:cart')


@login_required
def cart(request):
    user = request.user
    cart_products = Cart.objects.filter(user=user)

    # Display Total on Cart Page
    amount = decimal.Decimal(0)
    shipping_amount = decimal.Decimal(10)
    # using list comprehension to calculate total amount based on quantity and shipping
    cp = [p for p in Cart.objects.all() if p.user==user]
    if cp:
        for p in cp:
            temp_amount = (p.quantity * p.product.price)
            amount += temp_amount

    # Customer Addresses
    addresses = Address.objects.filter(user=user)

    context = {
        'cart_products': cart_products,
        'amount': amount,
        'shipping_amount': shipping_amount,
        'total_amount': amount + shipping_amount,
        'addresses': addresses,
    }
    return render(request, 'store/cart.html', context)


@login_required
def remove_cart(request, cart_id):
    if request.method == 'GET':
        c = get_object_or_404(Cart, id=cart_id)
        c.delete()
        messages.success(request, "Product removed from Cart.")
    return redirect('store:cart')


@login_required
def plus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        cp.quantity += 1
        cp.save()
    return redirect('store:cart')


@login_required
def minus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        # Remove the Product if the quantity is already 1
        if cp.quantity == 1:
            cp.delete()
        else:
            cp.quantity -= 1
            cp.save()
    return redirect('store:cart')

def checkoutPage(request):
    user = request.user
    cart_products = Cart.objects.filter(user=user)

    amount = decimal.Decimal(0)
    shipping_amount = decimal.Decimal(10)
    # using list comprehension to calculate total amount based on quantity and shipping
    cp = [p for p in Cart.objects.all() if p.user==user]
    if cp:
        for p in cp:
            temp_amount = (p.quantity * p.product.price)
            amount += temp_amount
    
    context={
        'cart_products':cart_products,
        'amount': amount,
        'shipping_amount': shipping_amount,
        'total_amount': amount + shipping_amount,
    }
    print("context",context)
    return render(request,'store/checkout.html',context)


@login_required
def checkout(request):
    user = request.user
    
    # Collecting delivery address details from POST request
    firstName = request.POST.get('firstName')
    lastName = request.POST.get('lastName')
    phoneNumber = request.POST.get('phoneNumber')
    city = request.POST.get('city')
    email = request.POST.get('email')
    country = request.POST.get('country')
    address_text = request.POST.get('address')

    # Creating Delivery Address object
    address = DeliveryAddress.objects.create(
        firstName=firstName,
        lastName=lastName,
        phoneNumber=phoneNumber,
        city=city,
        email=email,
        country=country,
        address=address_text,
    )

    # Creating a single order object
    order = Order.objects.create(user=user, deliveryAddress=address)

    # Get all products from the cart and create OrderItem for each
    cart = Cart.objects.filter(user=user)
    for cart_item in cart:
        OrderItem.objects.create(order=order, product=cart_item.product, quantity=cart_item.quantity)
        cart_item.delete()

    return redirect('store:orders')



       



@login_required
def orders(request):
    all_orders = Order.objects.filter(user=request.user).order_by('-ordered_date')
    return render(request, 'store/orders.html', {'orders': all_orders})

def logoutF(request):
    logout(request)
    return redirect('store:home')


def shop(request):

    all_categories = Category.objects.all() 

    products_paginator = Product.objects.filter(is_active=True) 
    paginator = Paginator(products_paginator, 100) 
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    context={
        'products':products,
        'all_categories':all_categories,
    }

    return render(request, 'store/shop.html',context)


def newArrivals(request):

    all_categories = Category.objects.all() 

    products_paginator = Product.objects.filter(is_active=True, new_arrival=True) 
    paginator = Paginator(products_paginator, 100) 
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    context={
        'products':products,
        'all_categories':all_categories,
    }

    return render(request, 'store/new_arrivals.html',context)


def saleView(request):

    all_categories = Category.objects.all() 

    products_paginator = Product.objects.filter(is_active=True, sale=True) 
    paginator = Paginator(products_paginator, 100) 
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    context={
        'products':products,
        'all_categories':all_categories,
    }

    return render(request, 'store/sale.html',context)


def test(request):
    return render(request, 'store/test.html')



# Views related to admin panel


def is_superuser(user):
    return user.is_superuser


@user_passes_test(is_superuser, login_url='store:admin_login')
def admin_index(request):
    if not request.user.is_authenticated:
        return redirect('store:admin_login')
    
    totalBrands = Brand.objects.all().count()
    totalCategories = Category.objects.all().count()
    totalProducts = Product.objects.all().count()
    totalOrders = Order.objects.all().count()
    totalCustomers = User.objects.exclude(is_superuser=True).count()
  

    context = {
        'totalBrands':totalBrands,
        'totalCategories':totalCategories,
        'totalProducts':totalProducts,
        'totalOrders':totalOrders,
        'totalCustomers':totalCustomers,
       
    }

    return render(request,'admin/admin_index.html', context)


# Admin login view
def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('store:admin_index')  # Replace with your admin dashboard URL name
        else:
            return render(request, 'admin/admin_login.html', {'error': 'Invalid credentials or not an admin.'})
    print("this is admin login---")
    return render(request, 'admin/admin_login.html')





def addBrand(request):
    if not request.user.is_authenticated:
        return redirect('store:admin_login')
    
    if request.method == "POST":
        try:
            brandData = {
                'name': request.POST.get('name'),
                'Date': request.POST.get('Date'),
                'brand_image': request.FILES.get('brand_image')  
            }

            brandObject = Brand(**brandData)
            brandObject.save()
            
            messages.success(request, 'Record Saved successfully.')
            return redirect('store:addBrand')
        except Exception as e:       
            messages.error(request, f'Some Error Occurred While Saving Data: {str(e)}')
    
    brandData = Brand.objects.all()
    
    context={
        'brandData':brandData,
    }

    return render(request,'admin/add_brand.html',context)


def editBrand(request, id):
    if not request.user.is_authenticated:
        return redirect('store:admin_login')

    if request.method == "POST":
        try:
            editedBrandData = Brand.objects.get(id=id)
            editedBrandData.name = request.POST.get('name')
            editedBrandData.Date = request.POST.get('Date')

            if request.FILES.get('brand_image'):
                editedBrandData.brand_image = request.FILES.get('brand_image')

            editedBrandData.save()

            messages.success(request, 'Record Updated successfully.')
            return redirect('store:addBrand')
        except Exception as e:  
            messages.error(request, f'Error updating record: {str(e)}')

    brandData = Brand.objects.all()
    return render(request, 'admin/add_brand.html', {'brandData': brandData})


def deleteBrand(request, id):
    if not request.user.is_authenticated:
        return redirect('store:admin_login')
    
    brandData = Brand.objects.filter(id=id)
    brandData.delete()
    return redirect('store:addBrand')


def addBaseType(request):
    if not request.user.is_authenticated:
        return redirect('store:admin_login')
    
    if request.method == "POST":
        try:
            typeData = {
                'type_name': request.POST.get('type_name'),
                'Date': request.POST.get('Date'),
            }

            typeObject = BaseType(**typeData)
            typeObject.save()
            
            messages.success(request, 'Record Saved successfully.')
            return redirect('store:addBaseType')
        except Exception as e:       
            messages.error(request, f'Some Error Occurred While Saving Data: {str(e)}')
    
    typeData = BaseType.objects.all()
    
    context={
        'typeData':typeData,
    }

    return render(request,'admin/add_basetype.html',context)


def deleteBaseType(request, id):
    if not request.user.is_authenticated:
        return redirect('store:admin_login')
    
    typeData = BaseType.objects.filter(id=id)
    typeData.delete()

    return redirect('store:addBaseType')



def addCategory(request):
    if not request.user.is_authenticated:
        return redirect('store:admin_login')

    if request.method == "POST":
        try:
            
            brand_id = request.POST.get('brand')
            brand_object = Brand.objects.get(id=brand_id)  

            
            categoryData = {
                'brand': brand_object,  
                'title': request.POST.get('title'),
                'slug': request.POST.get('slug'),
                'description': request.POST.get('description'),
                'is_active': request.POST.get('is_active') == 'on',  
                'is_featured': request.POST.get('is_featured') == 'on',  
                'category_image': request.FILES.get('category_image')  
            }

           
            categoryObject = Category(**categoryData)
            categoryObject.save()

            messages.success(request, 'Record Saved successfully.')
            return redirect('store:addCategory')

        except Exception as e:
            messages.error(request, f'Some Error Occurred While Saving Data: {str(e)}')

   
    categoryData = Category.objects.all()
    brands = Brand.objects.all()

    context = {
        'brands': brands,
        'categoryData': categoryData,
    }

    return render(request, 'admin/add_category.html', context)



def editCategory(request, category_id):
    if not request.user.is_authenticated:
        return redirect('store:admin_login')

    # Get the category object to edit
    category = get_object_or_404(Category, id=category_id)

    if request.method == "POST":
        try:
            # Update category fields
            brand_id = request.POST.get('brand')
            brand_object = Brand.objects.get(id=brand_id) if brand_id else None

            category.brand = brand_object
            category.title = request.POST.get('title')
            category.slug = request.POST.get('slug')
            category.description = request.POST.get('description')
            category.is_active = request.POST.get('is_active') == 'on'
            category.is_featured = request.POST.get('is_featured') == 'on'

            # Update image only if a new one is provided
            if request.FILES.get('category_image'):
                category.category_image = request.FILES.get('category_image')

            category.save()

            messages.success(request, 'Category updated successfully.')
            return redirect('store:addCategory')
        except Exception as e:
            messages.error(request, f'Error occurred while updating the category: {str(e)}')

    return redirect('store:addCategory')


def deleteCategory(request, id):
    if not request.user.is_authenticated:
        return redirect('store:admin_login')
    
    categoryData = Category.objects.filter(id=id)
    categoryData.delete()

    return redirect('store:addCategory')


def addProduct(request):
    if not request.user.is_authenticated:
        return redirect('store:admin_login')

    if request.method == "POST":
        try:
            
            category_id = request.POST.get('category')
            category_object = Category.objects.get(id=category_id)  

            type_id = request.POST.get('basetype')
            type_object = BaseType.objects.get(id=type_id)  
            
            productData = {
                'category': category_object,
                'basetype': type_object,  
                'title': request.POST.get('title'),
                'width': request.POST.get('width'),
                'length': request.POST.get('length'),
                'quantity': request.POST.get('quantity'),
                'short_description': request.POST.get('short_description'),
                'detail_description': request.POST.get('detail_description'),
                'price': request.POST.get('price'),
                'is_active': request.POST.get('is_active') == 'on',  
                'is_featured': request.POST.get('is_featured') == 'on',  
                'new_arrival': request.POST.get('new_arrival') == 'on',  
                'sale': request.POST.get('sale') == 'on',  
                'product_image': request.FILES.get('product_image')  
            }

           
            productObject = Product(**productData)
            productObject.save()

            messages.success(request, 'Record Saved successfully.')
            return redirect('store:addProduct')

        except Exception as e:
            messages.error(request, f'Some Error Occurred While Saving Data: {str(e)}')

    
    category = Category.objects.all()
    productData = Product.objects.all()
    basetype = BaseType.objects.all()

    context = {
        'category': category,
        'productData': productData,
        'basetype':basetype,
    }

    return render(request, 'admin/add_product.html',context)


def editProduct(request, product_id):
    if not request.user.is_authenticated:
        return redirect('store:admin_login')

    
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        try:
            # Update category fields
            category_id = request.POST.get('category')
            category_object = Category.objects.get(id=category_id) if category_id else None

            type_id = request.POST.get('basetype')
            type_object = BaseType.objects.get(id=type_id) if type_id else None

            product.category = category_object
            product.basetype = type_object
            product.title = request.POST.get('title')
            product.width = request.POST.get('width')
            product.length = request.POST.get('length')
            product.quantity = request.POST.get('quantity')
            product.short_description = request.POST.get('short_description')
            product.detail_description = request.POST.get('detail_description')
            product.price = request.POST.get('price')
            product.is_active = request.POST.get('is_active') == 'on'
            product.is_featured = request.POST.get('is_featured') == 'on'
            product.sale = request.POST.get('sale') == 'on'
            product.new_arrival = request.POST.get('new_arrival') == 'on'

            # Update image only if a new one is provided
            if request.FILES.get('product_image'):
                product.product_image = request.FILES.get('product_image')

            product.save()

            messages.success(request, 'Product updated successfully.')
            return redirect('store:addProduct')
        except Exception as e:
            messages.error(request, f'Error occurred while updating the product: {str(e)}')

    return redirect('store:addProduct')


def deleteProduct(request, id):
    if not request.user.is_authenticated:
        return redirect('store:admin_login')
    
    productData = Product.objects.filter(id=id)
    productData.delete()

    return redirect('store:addProduct')


def allCustomers(request):
    if not request.user.is_authenticated:
        return redirect('store:admin_login')
    
    userData = User.objects.exclude(is_superuser=True)
    print("userData",userData)

    context={
        'userData':userData,
    }

    return render(request,'admin/customers.html',context)



def allOrders(request):
    if not request.user.is_authenticated:
        return redirect('store:admin_login')
    
    orderData = Order.objects.all().order_by('-ordered_date')

    context={
        'orderData':orderData,
    }

    return render(request,'admin/all_orders.html',context)


def editStatus(request, id):
    if not request.user.is_authenticated:
        return redirect('store:admin_login')

    editedOrder = Order.objects.get(id=id)
    new_status = request.POST.get('status')
    payment_status = request.POST.get('payment_status')

    # Check if status is changing to "Delivered" and quantity hasn't been deducted yet
    if new_status == 'Delivered' and not editedOrder.quantity_deducted:
        # Deduct product quantities based on OrderItems
        for item in editedOrder.items.all():
            product = item.product
            product.quantity = int(product.quantity) - item.quantity
            product.save()

        # Mark as deducted to avoid multiple deductions
        editedOrder.quantity_deducted = True

    # If status changes back from "Delivered," reset quantity deduction flag
    elif editedOrder.status == 'Delivered' and new_status != 'Delivered' and editedOrder.quantity_deducted:
        # Add the quantity back if the order is no longer delivered
        for item in editedOrder.items.all():
            product = item.product
            product.quantity = int(product.quantity) + item.quantity
            product.save()

        editedOrder.quantity_deducted = False

    # Update the order status
    editedOrder.status = new_status
    editedOrder.payment_status = payment_status
    editedOrder.save()

    messages.success(request, 'Status updated successfully.')
    return redirect('store:allOrders')




@login_required
def addReview(request):
    detail=request.POST.get('detail')
    product_id = request.POST.get('product_id')

    if product_id and detail:
        product = Product.objects.get(id=product_id)
    
    Review.objects.create(
        user=request.user,
        detail=detail,
        product=product,
        date=date.today()
    )

    return redirect('store:product_detail', product_id)
