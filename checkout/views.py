from django.shortcuts import render
from products.context_processors import zoyro
from django.contrib.auth.models import User
from delivery.models import DeliveryAddress
from products.models import Product

def checkout_view(request):
    data = zoyro(request)
    if not request.user.is_authenticated:
        guest_user_id = request.session.get('guest_user_id', {})
        if guest_user_id:
            user = User.objects.get(id=guest_user_id)
            address = DeliveryAddress.objects.filter(user=user)
        else:
            address = {}
    else:
        address = request.user.address.all()

    return render(request, 'checkout/checkout.html',{
        'address':address,
    })

def direct_checkout(request, product_slug, quantity, size):
    product = Product.objects.get(slug=product_slug)
    if not request.user.is_authenticated:
        guest_user_id = request.session.get('guest_user_id', {})
        if guest_user_id:
            user = User.objects.get(id=guest_user_id)
            address = DeliveryAddress.objects.filter(user=user)
        else:
            address = {}
    else:
        address = request.user.address.all()
    product_disccount = product.price* quantity - product.offer_price* quantity
    subtotal = product.offer_price * quantity
    total_cost = subtotal + 70
    
    return render(request, 'checkout/direct_checkout.html', {
        'address':address,
        'product_disccount':product_disccount,
        'total_cost':total_cost,
        'product':product,
        "quantity":quantity,
        'subtotal':subtotal,
        'size':size,
    })
