from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from products.models import Product
from cart.models import Cart, CartItem
from django.views.decorators.csrf import csrf_exempt
import json
from .models import CartItem

# Create your views here.


@csrf_exempt 
def add_to_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            slug = data.get('slug')
            size = data.get('size')
            qty = int(data.get('quantity', 1))

            if not slug or not size:
                return JsonResponse({'error': 'Missing required fields.'}, status=400)

            product = get_object_or_404(Product, slug=slug)

            if not request.user.is_authenticated:
                cart = request.session.get('cart', {})
                cart_id = f"{slug}_{size}"

                if cart_id in cart:
                    cart[cart_id]['quantity'] += qty
                else:
                    cart[cart_id] = {
                        'product_id': product.id,
                        'price': float(product.price),
                        'offer_price': float(product.offer_price),
                        'size': size,
                        'quantity': qty,
                    }

                request.session['cart'] = cart
                request.session.modified = True

                return JsonResponse({
                    'message': 'Product added to cart successfully!',
                    'productName': product.title,
                    'itemCount': sum(item['quantity'] for item in cart.values())
                }, status=200)

            # Handle authenticated user cart
            else:
                cart, _ = Cart.objects.get_or_create(user=request.user)
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    size=size
                )

                if created:
                    cart_item.quantity = qty
                else:
                    cart_item.quantity += qty

                cart_item.save()

                total_items = CartItem.objects.filter(cart=cart).count()

                return JsonResponse({
                    'message': 'Product added to cart successfully!',
                    'productName': product.title,
                    'itemCount': total_items
                }, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

        
    
    

from products.context_processors import zoyro
@csrf_exempt
def update_cart_item(request):
    if request.method == "POST":
        data = json.loads(request.body)
        item_id = data.get("item_id")
        quantity = data.get("quantity")
    # Handle authenticated user cart
    if request.user.is_authenticated:
        try:
            item = CartItem.objects.get(id=item_id)
            item.quantity = quantity
            item.save()
            context = zoyro(request)
            
            serialized_context = {
                "sub_total": context.get("sub_total"),
                "delivery_charge": (context.get("delivery_charge")),
                "total": (context.get("total")),
                "total_saving": (context.get("total_saving")),
                "item_count": context.get("item_count"),
                # Add more fields as needed, ensure they're serializable
            }
            return JsonResponse({"status": "success", 'context':serialized_context})
        except CartItem.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Item not found"}, status=404)
    else:
        # Handle the case for unauthenticated users (session cart)
        cart = request.session.get('cart', {})
        if str(item_id) in cart:
            cart[str(item_id)]['quantity'] = quantity
            request.session['cart'] = cart
            request.session.modified = True
            context = zoyro(request)
            
            serialized_context = {
                "sub_total": context.get("sub_total"),
                "delivery_charge": (context.get("delivery_charge")),
                "total": (context.get("total")),
                "total_saving": (context.get("total_saving")),
                "item_count": context.get("item_count"),
                # Add more fields as needed, ensure they're serializable
            }
            return JsonResponse({"status": "success",'context':serialized_context})
        else:
            return JsonResponse({"status": "error", "message": "Item not found in session cart"}, status=404)



def remove_from_cart(request):
    if request.method == "POST":
        data = json.loads(request.body)
        item_id = data.get("item_id")
        # Handle authenticated user cart
        if request.user.is_authenticated:
            try:
                item = get_object_or_404(CartItem, id=item_id, cart__user = request.user)
                item.delete()
                return JsonResponse({"status": "success", "message": "Item removed from cart."}, status=200)
            except CartItem.DoesNotExist:
                return JsonResponse({"status": "error", "message": "Item not found"}, status=404)
        else:
            cart = request.session.get('cart', {})
            if str(item_id) in cart:
                del cart[str(item_id)]
                request.session['cart'] = cart
                request.session.modified = True
                return JsonResponse({"status": "success", "message": "Item removed from cart."}, status=200)
            else:
                return JsonResponse({"status": "error", "message": "Item not found in session cart"}, status=404)