from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from products.models import Product
from banners.models import Banner, SmallBanner

def home_view(request):
    products = Product.objects.filter(is_active=True).order_by('-click_count')[:10]
    top_savers_products = Product.objects.all().order_by('-discount')[:6]
    banners = Banner.objects.filter(is_active=True).order_by('position')
    small_banners = SmallBanner.objects.filter(is_active=True).order_by('position')
    return render(request, 'home/home.html',{
        'products': products,
        'top_savers_products': top_savers_products,
        'banners': banners,
        'small_banners': small_banners,
    })

def contact_view(r):
    pass

def about_view(r):
    pass