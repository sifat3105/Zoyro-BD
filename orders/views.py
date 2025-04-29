from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from decimal import Decimal
from django.urls import reverse

from products.models import Product
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
            shipping_method=address.get_full_address(),
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

        return redirect('orders:order_confirmed', order_number=order.order_number)

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
    

def order_confirmed(request, order_number):
    return render(request, 'order/order_confirmed.html', {'order_number': order_number})


