from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from products.models import Product
from banners.models import Banner, SmallBanner

def home_view(request):
    if request.GET.get('import_dummy') == 'true':
        a = import_dummy_products(request)
        print(a)
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



import requests
from django.shortcuts import render
from products.models import Category, SubCategory, Brand, Product, ProductImage
from django.utils.text import slugify
from datetime import datetime

def import_dummy_products(request):
    # API URL
    api_url = "https://dummyjson.com/products?limit=17&skip=13"  # skip first 13, get next 17
    
    try:
        # Make the API request
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        
        imported_count = 0
        
        # Process each product from the API
        for api_product in data.get('products', []):
            # Determine category based on API data
            category_name = api_product.get('category', 'uncategorized').title()
            category, _ = Category.objects.get_or_create(
                name=category_name,
                defaults={
                    'description': f"{category_name} products",
                    'slug': slugify(category_name)
                }
            )
            
            # Create a subcategory with the same name as category if none exists
            subcategory, _ = SubCategory.objects.get_or_create(
                category=category,
                name=category_name,
                defaults={
                    'description': f"{category_name} products",
                    'slug': slugify(f"{category_name}-products")
                }
            )
            
            # Get or create the brand
            brand_name = api_product.get('brand', 'Unknown')
            brand, _ = Brand.objects.get_or_create(
                name=brand_name,
                defaults={
                    'slug': slugify(brand_name),
                    'description': f"{brand_name} brand products"
                }
            )
            
            # Calculate offer price if there's a discount
            price = float(api_product.get('price', 0))
            discount_percentage = float(api_product.get('discountPercentage', 0))
            offer_price = round(price * (1 - discount_percentage / 100), 2) if discount_percentage else None
            
            # Determine availability status
            stock = api_product.get('stock', 0)
            if stock > 10:
                availability = 'in_stock'
            elif stock > 0:
                availability = 'low_stock'
            else:
                availability = 'out_of_stock'
            
            # Create the product
            product, created = Product.objects.get_or_create(
                sku=api_product.get('sku', f"DUMMY-{api_product['id']}"),  # Use SKU or fallback to ID
                defaults={
                    'title': api_product.get('title', 'Untitled Product'),
                    'product_code': api_product.get('sku', f"DUMMY-{api_product['id']}"),
                    'price': price,
                    'offer_price': offer_price,
                    'discount': discount_percentage,
                    'quantity': stock,
                    'quick_overview': api_product.get('description', '')[:200],
                    'additional_description': api_product.get('description', ''),
                    'availability': availability,
                    'category': category,
                    'subcategory': subcategory,
                    'brand': brand,
                    'is_active': True,
                    'slug': slugify(api_product.get('title', f"product-{api_product['id']}"))
                }
            )
            
            if created:
                imported_count += 1
        
        message = f"Successfully imported {imported_count} products (last 17 from API)"
        success = True
        
    except requests.RequestException as e:
        message = f"Error fetching data from API: {str(e)}"
        success = False
    except Exception as e:
        message = f"Error processing data: {str(e)}"
        success = False
    
    context = {
        'message': message,
        'success': success,
        'imported_count': imported_count if success else 0
    }
    
    return context