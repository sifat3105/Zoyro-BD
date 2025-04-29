from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.views import create_guest_user
from .models import DeliveryAddress

def create_delivery_address_view(request):
    if request.method == 'POST':
        # Get all fields from request
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        email = request.POST.get('email', '').strip()
        address_type = request.POST.get('address_type', 'home')
        division = request.POST.get('division', '').strip()
        district = request.POST.get('district', '').strip()
        upazila = request.POST.get('upazila', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        delivery_area = request.POST.get('delivery_area', '').strip()
        is_default = request.POST.get('is_default', 'false').lower() == 'true'
        
        # Validate required fields
        if not all([first_name, last_name, phone_number, division, district, upazila, postal_code, delivery_area]):
            messages.error(request, "Please fill all required fields")
            return redirect("checkout:checkout_view")
        
        try:
            user = request.user if request.user.is_authenticated else None
            if not request.user.is_authenticated:
                if not email:
                    messages.error(request, "Email is required for guest users")
                    return redirect("checkout:checkout_view")
                user = create_guest_user(
                    email=email,
                    first_name=first_name,
                    last_name=last_name
                )
                guest_user_id = user.id
                request.session['guest_user_id'] = guest_user_id
                request.session.modified = True

                
            full_name = f"{first_name} {last_name}"
            DeliveryAddress.objects.create(
                user=user,
                full_name=full_name,
                phone_number=phone_number,
                email=email if email else None,
                address_type=address_type,
                division=division,
                district=district,
                upazila=upazila,
                postal_code=postal_code,
                delivery_area=delivery_area,
                is_default=is_default,
            )
            messages.success(request, "Delivery address created successfully!")
        except Exception as e:
            messages.error(request, f"Error creating address: {str(e)}")
        
        return redirect("checkout:checkout_view")