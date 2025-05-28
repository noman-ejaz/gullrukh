from .models import Category, Cart, Brand


def store_menu(request):
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.all()
    context = {
        'categories_menu': categories,
        'brands':brands,
    }
    return context

def cart_menu(request):
    if request.user.is_authenticated:
        cart_items= Cart.objects.filter(user=request.user)
        context = {
            'cart_items': cart_items,
        }
    else:
        context = {}
    return context