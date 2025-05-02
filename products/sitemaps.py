from django.contrib.sitemaps import Sitemap
from .models import Product, Category,SubCategory
from django.urls import reverse

class ProductSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.9

    def items(self):
        return Product.objects.all()

    def lastmod(self, obj):
        return obj.updated_at

class CategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return obj.get_absolute_url()
    

class SubCategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return SubCategory.objects.all()

    def location(self, obj):
        return obj.get_absolute_url()

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        return ['home', 'contact', 'about']

    def location(self, item):
        return reverse(f'home:{item}')
