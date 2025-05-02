from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from decimal import Decimal
from django.urls import reverse
from products.context_processors import zoyro
from products.models import Product,ApparelSize
from delivery.models import DeliveryAddress
from .models import Order, OrderItem


def cod_create(request, quantity, size, product_slug, address_id):
    try:
        subtotal = request.GET.get('subtotal')
        total_cost = request.GET.get('total_cost')

        if not subtotal or not total_cost:
            return JsonResponse({'success': False, 'message': 'Missing subtotal or total cost.'}, status=400)

        subtotal = Decimal(subtotal)
        total_cost = Decimal(total_cost)

        address = get_object_or_404(DeliveryAddress, id=address_id)
        product = get_object_or_404(Product, slug=product_slug)

        order = Order.objects.create(
            customer=address.user,
            payment_method='cash_on_delivery',
            status='pending',
            shipping_address=address.get_full_address(),
            number=address.phone_number,
            shipping_cost=Decimal('70.00'),
            discount_amount=(product.price * quantity) - subtotal,
            total_amount=total_cost,
        )

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            size=size,
            unit_price=subtotal,
        )
    
        product.quantity -= quantity
        size=size.upper()
        apparel_size =  ApparelSize.objects.get(product=product, size=size)
        apparel_size.quantity -= quantity
        apparel_size.save()
        product.save() 

        return redirect('orders:order_confirmed', order_number=order.order_number)

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
    

def cod_create2(request, address_id):
    address = get_object_or_404(DeliveryAddress, id=address_id)
    try:
        address = address
        data = zoyro(request)
        shipping_cost = Decimal(70.00)
        

        order = Order.objects.create(
            customer=address.user,
            payment_method='cash_on_delivery',
            status='pending',
            shipping_address=address.get_full_address(),
            number=address.phone_number,
            shipping_cost= shipping_cost,
            discount_amount= data['discount'],
            total_amount=data['sub_total'] + shipping_cost,
        )
        try:
            if request.user.is_authenticated:
                
                for item in data['cart_items']:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        size=item.size,
                        unit_price=item.product.price,  # Actual product price
                    )
                    product = item.product
                    product.quantity -= item.quantity
                    size=item.size.upper()
                    apparel_size =  ApparelSize.objects.get(product=product, size=size)
                    apparel_size.quantity -= item.quantity
                    apparel_size.save()
                    product.save() 
                    item.delete()
            else:
                # Anonymous user - cart_items is from session
                for cart_key, item_data in data['cart_items'].items():
                    OrderItem.objects.create(
                        order=order,
                        product=item_data['product'],
                        quantity=item_data['quantity'],
                        size=item_data['size'],
                        unit_price=item_data['product'].price,
                    )
                    product = item_data['product']
                    product.quantity -= item_data['quantity']
                    size=item_data['size'].upper()
                    print(size)
                    apparel_size =  ApparelSize.objects.get(product=product, size=size)
                    apparel_size.quantity -= item_data['quantity']
                    apparel_size.save()
                    product.save()

                    if 'cart' in request.session:
                        del request.session['cart']
                        request.session.modified = True

        except Exception as e:
            # Handle any errors (log them, notify admin, etc.)
            print(f"Error creating order items: {str(e)}")
            raise
        

        return redirect('orders:order_confirmed', order_number=order.order_number)

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
    

def order_confirmed(request, order_number):
    return render(request, 'order/order_confirmed.html', {'order_number': order_number})

def order_detail(request):
    order_number = request.GET.get('order_id')
    context = {}
    
    if order_number:
        try:
            order = Order.objects.get(order_number=order_number)
            subtotal = order.total_amount - order.tax_amount - order.shipping_cost + order.discount_amount
            context['order'] = order
            context['subtotal'] = subtotal
        except Order.DoesNotExist:
            context['error'] = f"Order {order_number} not found"
    
    return render(request, 'order/order_detail.html', context)


