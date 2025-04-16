from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.http import urlencode
from products.models import Product, Category
from . utils import smart_product_search
import random, string


def product_search(request):
    query = request.GET.get('q', '')

    if query:   
        products = smart_product_search(query)
    else:
        products = Product.objects.all()
    categories = Category.objects.filter(products__in=products).distinct()
    context = {
        'products': products,
        'query': query,
        "categories":categories
    }
    
    return render(request, 'product/products.html', context)

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
    return HttpResponseRedirect(f"{reverse('product_search')}?{query_string}")



