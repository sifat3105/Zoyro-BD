from django.shortcuts import render, get_object_or_404
from .models import Product,ProductImage, Category, SubCategory
# from reviews.models import review

def product_details(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    product.click_count +=1
    product.save()
    images = product.images.all()
    domain = request.get_host()
    apparel_sizes = product.apparel_sizes.all()
    apparel_size_list = [size.size.lower() for size in product.apparel_sizes.all()]
    save = product.price - product.offer_price
    return render(request, 'product/product_details.html',{
        'product': product,
        'images':images,
        'save':save,
        'domain':domain,
        'apparel_sizes':apparel_sizes,
        'apparel_size_list':apparel_size_list,
        'all_sizes': ['xs', 's', 'm', 'l', 'xl', 'xxl'],
    })