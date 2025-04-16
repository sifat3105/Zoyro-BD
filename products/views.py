from django.shortcuts import render, get_object_or_404
from .models import Product,ProductImage, Category, SubCategory
# from reviews.models import review

def product_details(request):
    product_slug = request.GET.get('slug')
    product = get_object_or_404(Product, slug=product_slug)
    product.click_count +=1
    product.save
    images = product.images.all()
    return render(request, 'product/product_details.html',{
        'product': product,
        'images':images,
    })