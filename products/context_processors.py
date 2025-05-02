from accounts.views import create_guest_user
from django.shortcuts import get_object_or_404
from cart.models import Cart
from products.models import Product, Category,SubCategory
from django.conf import settings
from decimal import Decimal


def zoyro(request):
    categories = Category.objects.all()
    sobcategories = SubCategory.objects.all()
    domain = request.get_host()

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        total_price = Decimal(cart.get_total_price())
        sub_total = Decimal(cart.get_total_offer_price())
        discount = int(((total_price - sub_total) / total_price) * 100) if total_price and sub_total else 0
        dis_price = int(total_price - sub_total)
        total_saving = f"{dis_price} ({discount}%)"
        cart_items = cart.items.all()
        for item in cart_items:
            i_size = item.size.upper()
            item.max_quantity = item.product.get_quantity_for_size(i_size)
        wishlist_items = None
        context = {
            'nav_categories': categories, 
            'nav_sobcategories': sobcategories, 
            'sub_total': sub_total if cart else '0.00',
            'total_saving': total_saving,
            'delivery_charge': '70.00' if cart else '0.00',
            'total': round(sub_total + Decimal(70.00), 2) if cart else 0.00,
            'cart_items': cart_items,
            'item_count': cart.get_total_item_count(),
            'domain': domain,
            'GOOGLE_CLIENT_ID': settings.GOOGLE_CLIENT_ID,
            'wishlist_items':wishlist_items,
            'discount': dis_price,
        }
        
    else:
        cart = request.session.get('cart', {})
        total_price = sum(Decimal(item.get('price', 0)) * Decimal(item.get('quantity', 0)) for item in cart.values())
        sub_total = round(Decimal(sum(Decimal(item.get('offer_price', 0)) * Decimal(item.get('quantity', 0)) for item in cart.values())),2)
        discount = int(((total_price - sub_total) / total_price) * 100) if total_price and sub_total else 0
        dis_price = round(Decimal(total_price - sub_total),2)
        total_saving = f"{dis_price} ({discount}%)"
        wishlist_items = None
        cart_items = {}
        for item_id, item in cart.items():
            try:
                product = get_object_or_404(Product, id=item.get('product_id'))
                if product:
                    size = item.get('size', '')
                    cart_items[f"AnonymousUser{item_id}"] = {
                        'id': item_id,
                    
                        'product': product,
                        'quantity': item.get('quantity', 0),
                        'size': size,
                        'max_quantity': product.get_quantity_for_size(size.upper())
                    }
            except Exception as e:
                print(f"Error processing cart item {item_id}: {e}")
                continue
         
        context = {
            'nav_categories': categories,
            'nav_sobcategories': sobcategories, 
            'sub_total': sub_total if cart else '0.00',
            'total_saving': total_saving,
            'delivery_charge': '70.00' if cart else '0.00',
            'total': round(sub_total + Decimal(70.00), 2) if cart else 0.00,
            'cart_items': cart_items,
            'item_count': sum(int(item['quantity']) for item in cart_items.values()),
            'domain': domain,
            'GOOGLE_CLIENT_ID': settings.GOOGLE_CLIENT_ID,
            'wishlist_items':wishlist_items,
            'discount': dis_price,
        }
    
    return context

