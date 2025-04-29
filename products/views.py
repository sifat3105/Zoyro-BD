from django.shortcuts import render, get_object_or_404
from .models import Product,ProductImage, Category, SubCategory
from django.db.models import Case, When

# from reviews.models import review

def product_details(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    recommended_products = None
    product = get_object_or_404(Product, slug=product_slug)
    product.click_count +=1
    product.save()
    images = product.images.all()
    domain = request.get_host()
    apparel_sizes = product.apparel_sizes.all()
    available_sizes = {apparel.size.lower(): apparel.quantity for apparel in apparel_sizes}
    size_quantities = {apparel.size.lower(): apparel.quantity for apparel in apparel_sizes}
    size_quantities = dict(size_quantities)
    save = product.price - product.offer_price
    
    return render(request, 'product/product_details.html',{
        'product': product,
        'images':images,
        'save':save,
        'domain':domain,
        'available_sizes':available_sizes,
        'all_sizes': ['xs', 's', 'm', 'l', 'xl', 'xxl'],
        'recommended_products': recommended_products,
        'size_quantities': size_quantities,
    })