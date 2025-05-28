from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Brand(models.Model):
    name = models.CharField(max_length=150)
    brand_image = models.ImageField(upload_to='brand', blank=True, null=True)
    Date = models.DateTimeField()

    def __str__(self):
        return self.name
    


class BaseType(models.Model):
    type_name = models.CharField(max_length=150)
    Date = models.DateTimeField()

    def __str__(self):
        return self.type_name
    



class Address(models.Model):
    user = models.ForeignKey(User, verbose_name="addressUser", on_delete=models.CASCADE,default=False)
    locality = models.CharField(max_length=150, verbose_name="Location")
    city = models.CharField(max_length=150, verbose_name="City")
    state = models.CharField(max_length=150, verbose_name="State")

    def __str__(self):
        return self.locality


class Category(models.Model):
    brand = models.ForeignKey(Brand, verbose_name="Categoy Brand", on_delete=models.CASCADE, default=False)
    title = models.CharField(max_length=50, verbose_name="Category Title")
    slug = models.SlugField(max_length=55, verbose_name="Category Slug")
    description = models.TextField(blank=True, verbose_name="Category Description")
    category_image = models.ImageField(upload_to='category', blank=True, null=True, verbose_name="Category Image")
    is_active = models.BooleanField(verbose_name="Is Active?")
    is_featured = models.BooleanField(verbose_name="Is Featured?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created Date")

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ('-created_at', )

    def __str__(self):
        return self.title


class Product(models.Model):
    category = models.ForeignKey(Category, verbose_name="Product Categoy", on_delete=models.CASCADE)
    basetype = models.ForeignKey(BaseType, verbose_name="Base Type", on_delete=models.CASCADE,default=False)

    title = models.CharField(max_length=150, verbose_name="Product Title")
    quantity = models.CharField(max_length=255,default=False)
    length = models.CharField(max_length=255,default=False)
    width = models.CharField(max_length=255,default=False)
    short_description = models.TextField(verbose_name="Short Description")
    detail_description = models.TextField(blank=True, null=True, verbose_name="Detail Description")
    product_image = models.ImageField(upload_to='product', blank=True, null=True, verbose_name="Product Image")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(verbose_name="Is Active?")
    is_featured = models.BooleanField(verbose_name="Is Featured?")
    new_arrival = models.BooleanField(default=False)
    sale = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created Date")

    class Meta:
        verbose_name_plural = 'Products'
        ordering = ('-created_at', )

    def __str__(self):
        return self.title


class Cart(models.Model):
    user = models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE,default=False)
    product = models.ForeignKey(Product, verbose_name="Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantity")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created Date")

    def __str__(self):
        return str(self.user)
    
    # Creating Model Property to calculate Quantity x Price
    @property
    def total_price(self):
        return self.quantity * self.product.price


class DeliveryAddress(models.Model):
    firstName = models.CharField(max_length=500)
    lastName = models.CharField(max_length=500)
    phoneNumber = models.CharField(max_length=500)
    email = models.EmailField(max_length=500)
    city = models.CharField(max_length=500)
    country = models.CharField(max_length=500)
    address = models.CharField(max_length=500)
    


STATUS_CHOICES = (
    ('Pending', 'Pending'),
    ('Accepted', 'Accepted'),
    ('Packed', 'Packed'),
    ('On The Way', 'On The Way'),
    ('Delivered', 'Delivered'),
    ('Cancelled', 'Cancelled')
)

PAYMENT_CHOICES = (
    ('UnPaid', 'UnPaid'),
    ('Paid', 'Paid')
)


class Order(models.Model):
    user = models.ForeignKey(User, verbose_name="Order User", on_delete=models.CASCADE)
    deliveryAddress = models.ForeignKey(DeliveryAddress, verbose_name="Shipping Address", on_delete=models.CASCADE)
    ordered_date = models.DateTimeField(auto_now_add=True, verbose_name="Ordered Date")
    status = models.CharField(choices=STATUS_CHOICES, max_length=50, default="Pending")
    payment_status = models.CharField(choices=PAYMENT_CHOICES, max_length=50, default="UnPaid")
    quantity_deducted = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name="Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.title} ({self.quantity})"


class Review(models.Model):
    user = models.ForeignKey(User, verbose_name="reviewUser", on_delete=models.CASCADE,default=False)
    product = models.ForeignKey(Product, verbose_name="ProductReview", on_delete=models.CASCADE,related_name="reviews")
    detail=models.CharField(max_length=255,default=False)
    date = models.DateTimeField(auto_now_add=True, verbose_name="reviewdate")




   