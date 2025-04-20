from accounts.views import create_guest_user
from django.shortcuts import get_object_or_404
from cart.models import Cart
from products.models import Product
from django.conf import settings


def zoyro(request):
    domain = request.get_host()
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        total_price = float(cart.get_total_price())
        sub_total = float(cart.get_total_offer_price())
        discount = int(((total_price - sub_total) / total_price) * 100) if total_price and sub_total else 0
        dis_price = int(total_price - sub_total)
        total_saving = f"{dis_price} ({discount}%)"
        cart_items = cart.items.all()
        context = {
            'sub_total': sub_total if cart else '0.00',
            'total_saving': total_saving,
            'delivery_charge': '70.00' if cart else '0.00',
            'total': sub_total + 70.00 if cart else 0.00,
            'cart_items': cart_items,
            'item_count': cart.get_total_item_count(),
            'domain': domain,
            'GOOGLE_CLIENT_ID': settings.GOOGLE_CLIENT_ID,
        }
        print(context)
        
    else:
        cart = request.session.get('cart', {})
        total_price = sum(float(item.get('price', 0)) * float(item.get('quantity', 0)) for item in cart.values())
        sub_total = float(sum(float(item.get('offer_price', 0)) * float(item.get('quantity', 0)) for item in cart.values()))
        discount = int(((total_price - sub_total) / total_price) * 100) if total_price and sub_total else 0
        dis_price = int(total_price - sub_total)
        total_saving = f"{dis_price} ({discount}%)"
        
        cart_items = {}
        for item_id, item in cart.items():
            try:
                product = get_object_or_404(Product, id=item.get('product_id'))
                if product:
                    cart_items[f"AnonymousUser{item_id}"] = {
                        'id': item_id,
                    
                        'product': product,
                        'quantity': item.get('quantity', 0),
                        'size': item.get('size', ''),
                    }
            except Exception as e:
                print(f"Error processing cart item {item_id}: {e}")
                continue
        
        context = {
            'sub_total': sub_total if cart else '0.00',
            'total_saving': total_saving,
            'delivery_charge': '70.00' if cart else '0.00',
            'total': sub_total + 70.00 if cart else 0.00,
            'cart_items': cart_items,
            'item_count': sum(int(item['quantity']) for item in cart_items.values()),
            'domain': domain,
            'GOOGLE_CLIENT_ID': settings.GOOGLE_CLIENT_ID,
        }
    
    return context