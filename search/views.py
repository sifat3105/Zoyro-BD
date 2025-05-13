import random
import string
from django.db.models import Case, When, Count
from django.core.paginator import Paginator
from django.db.models import Case, When
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.http import urlencode

from products.models import Product, Category, Brand
from django.db.models import Q
from difflib import SequenceMatcher

from django.conf import settings

def js_search_products(request):
    query = request.GET.get('q', '')
    
    try:
        if not query:
            return JsonResponse({'js_products': []})
        
        products = Product.objects.filter(title__icontains=query)[:10]
        data = []
        for product in products:
            data.append({
                'id': product.id,
                'title': product.title,
                'price': str(product.price),
                'slug': product.slug,
                'image_url': product.default_image.url if product.default_image else settings.STATIC_URL + 'img/default-product.png'
            })
        
        return JsonResponse({'js_products': data})
    
    except Exception as e:
        print("ERROR:", e)
        return JsonResponse({'js_products': [], 'error': str(e)}, status=500)



def search_products(query, threshold=0.9):
    # First try to match with category/subcategory names
    category_matches = Category.objects.filter(
        Q(name__icontains=query) | 
        Q(subcategories__name__icontains=query)
    ).distinct()
    
    # Check for high similarity matches
    exact_category_matches = []
    for cat in category_matches:
        if SequenceMatcher(None, query.lower(), cat.name.lower()).ratio() >= threshold:
            exact_category_matches.append(cat)
        for subcat in cat.subcategories.all():
            if SequenceMatcher(None, query.lower(), subcat.name.lower()).ratio() >= threshold:
                exact_category_matches.append(cat)
                break
    
    # If we found high accuracy category matches, return products from those categories
    if exact_category_matches:
        return list(
            Product.objects.filter(
                Q(category__in=exact_category_matches) |
                Q(subcategory__category__in=exact_category_matches)
            ).values_list('id', flat=True)
        )
    
    # Fall back to product title search if no good category matches
    return list(
        Product.objects.filter(title__icontains=query).values_list('id', flat=True)
    )

def product_search(request):
    query = request.GET.get('q', '').strip()
    
    # Get filter parameters
    categories = request.GET.getlist('category')
    brands = request.GET.getlist('brand')
    price_range = request.GET.get('price')
    sort = request.GET.get('sort', 'relevance')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if query:
        # Semantic search
        product_ids = search_products(query)
        preserved_order = Case(
            *[When(pk=pk, then=pos) for pos, pk in enumerate(product_ids)]
        )
        products = Product.objects.filter(id__in=product_ids)
    else:
        products = Product.objects.all()
        preserved_order = None
    
    # Apply filters
    if categories:
        products = products.filter(category__id__in=categories)
    
    if brands:
        products = products.filter(brand__id__in=brands)
    
    if price_range:
        if price_range == '50_100':
            products = products.filter(offer_price__gte=50, offer_price__lte=100)
        elif price_range == '100_150':
            products = products.filter(offer_price__gte=100, offer_price__lte=150)
        elif price_range == '150_200':
            products = products.filter(offer_price__gte=150, offer_price__lte=200)
        elif price_range == '200_1000':
            products = products.filter(offer_price__gte=200, offer_price__lte=1000)
    
    # Custom price range
    if min_price:
        products = products.filter(offer_price__gte=float(min_price))
    if max_price:
        products = products.filter(offer_price__lte=float(max_price))
    
    # Apply sorting
    if sort == 'price_low':
        products = products.order_by('offer_price')
    elif sort == 'price_high':
        products = products.order_by('-offer_price')
    elif sort == 'discount':
        products = products.order_by('-discount')
    elif sort == 'name':
        products = products.order_by('title')
    elif sort == 'relevance' and preserved_order:
        products = products.order_by(preserved_order)
    else:
        products = products.order_by('-created_at')
    
    # Get filter options with counts
    filter_categories = Category.objects.filter(
        products__in=products
    ).annotate(
        product_count=Count('products')
    ).filter(product_count__gt=0)
    
    filter_brands = Brand.objects.filter(
        products__in=products
    ).annotate(
        product_count=Count('products')
    ).filter(product_count__gt=0)
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)
    
    context = {
        'products': products_page,
        'query': query,
        'categories': filter_categories,
        'brands': filter_brands,
        'selected_categories': [int(c) for c in categories],
        'selected_brands': [int(b) for b in brands],
        'selected_price': price_range,
        'selected_sort': sort,
        'min_price': min_price,
        'max_price': max_price,
    }
    
    return render(request, 'product/product_list.html', context)
    
def generate_random_string(length=10):
    """Generate a random string for query parameters like 'spm'."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def search_redirect(request):
    print(request.GET)
    query = request.GET.get('q', '').strip()  # Get search query and remove extra spaces
    
    if not query:
        return HttpResponseRedirect(reverse('product_search'))  # Redirect to search page if empty

    # Save search history in session
    search_history = request.session.get('search_history', [])  # Retrieve previous searches
    if query not in search_history:  # Avoid duplicates
        search_history.insert(0, query)  # Add new search to the beginning
        if len(search_history) > 10:  # Keep only the last 10 searches
            search_history.pop()
        request.session['search_history'] = search_history  # Save back to session

    # Generate dynamic parameters
    spm = f"a2a0e.tm{random.randint(100000, 999999)}.search.{random.randint(1, 5)}.{generate_random_string(10)}"
    keyori = random.choice(["ss", "search_suggestion", "history"])
    search_from = random.choice(["search_history", "homepage_suggestion", "category_recommendation"])
    sugg = f"{query}_0_{random.randint(1, 10)}"

    # Construct query parameters dynamically
    params = {
        "spm": spm,
        "q": query,
        "_keyori": keyori,
        "from": search_from,
        "sugg": sugg
    }

    # Encode parameters into URL
    query_string = urlencode(params)

    # Redirect to product search page with query parameters
    return HttpResponseRedirect(f"{reverse('search:product_search')}?{query_string}")





