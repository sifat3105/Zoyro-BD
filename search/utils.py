from openai import OpenAI, RateLimitError, APIError
from django.conf import settings
from products.models import Product, Category, SubCategory
import json
import time

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def smart_product_search(query):
    # Get current categories & subcategories
    categories = list(Category.objects.values_list('name', flat=True))
    subcategories = list(SubCategory.objects.values_list('name', flat=True))

    prompt = f"""..."""  # Your existing prompt here

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        filters = json.loads(response.choices[0].message.content)
        
    except RateLimitError:
        # Handle rate limit error - return unfiltered results or cached version
        return Product.objects.all()[:50]  # Fallback to limited results
        
    except APIError as e:
        if e.code == 'insufficient_quota':
            # Handle quota exceeded error
            return Product.objects.all()[:50]  # Fallback
        raise  # Re-raise other API errors
        
    except json.JSONDecodeError:
        filters = {
            "category": "",
            "subcategory": "",
            "keywords": "",
            "size": "",
            "price_min": "",
            "price_max": ""
        }

    # Rest of your filtering logic...
    return apply_filters(filters)

def apply_filters(filters):
    """Separate function for filter application"""
    products = Product.objects.all()
    
    if filters.get('category'):
        products = products.filter(category__name__icontains=filters['category'])
    
    # ... rest of your filter conditions ...
    
    return products