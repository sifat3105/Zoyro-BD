from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from products.sitemaps import ProductSitemap, CategorySitemap, StaticViewSitemap, SubCategory
from django.contrib import sitemaps
from django.contrib.sitemaps.views import sitemap

sitemaps_dict = {
    'products': ProductSitemap,
    'categories': CategorySitemap,
    # 'subcategories': SubCategory,
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('auth/', include('social_django.urls', namespace='social_zoyro')),
    path('account/', include('accounts.urls', namespace='accounts')),
    path('dashboard/', include('admin_dashboard.urls', namespace='admin_dashboard')),
    path('delivery/', include('delivery.urls', namespace='delivery')),
    path('cart/', include('cart.urls', namespace='cart')),
    path('checkout/', include('checkout.urls', namespace='checkout')),
    path('', include('home.urls', namespace='home')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('payments/', include('payments.urls', namespace='payments')),
    path('products/', include('products.urls', namespace='products')),
    path('reviews/', include('reviews.urls', namespace='reviews')),
    path('', include('search.urls', namespace='search')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps_dict}, name='sitemap'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
