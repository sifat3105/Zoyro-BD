import openai
from django.conf import settings
from products.models import Product, Category, SubCategory

openai.api_key = settings.OPENAI_API_KEY

def smart_product_search(query):
    # Get current categories & subcategories
    categories = list(Category.objects.values_list('name', flat=True))
    subcategories = list(SubCategory.objects.values_list('name', flat=True))

    prompt = f"""
You are a product search assistant for an e-commerce store.

These are the categories: {', '.join(categories)}
These are the subcategories: {', '.join(subcategories)}

Given the query: "{query}", extract:
- category
- subcategory
- keywords
- size
- price_min
- price_max

Return result in JSON like:
{{
  "category": "",
  "subcategory": "",
  "keywords": "",
  "size": "",
  "price_min": "",
  "price_max": ""
}}
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    filters = json.loads(response.choices[0].message.content)

    # Now apply the filters to the Product model
    products = Product.objects.all()

    if filters.get('category'):
        products = products.filter(category__name__icontains=filters['category'])

    if filters.get('subcategory'):
        products = products.filter(subcategory__name__icontains=filters['subcategory'])

    if filters.get('size'):
        products = products.filter(apparel_size__iexact=filters['size'])

    if filters.get('keywords'):
        for kw in filters['keywords'].split(','):
            products = products.filter(title__icontains=kw.strip())

    if filters.get('price_min'):
        products = products.filter(price__gte=float(filters['price_min']))

    if filters.get('price_max'):
        products = products.filter(price__lte=float(filters['price_max']))

    return products
