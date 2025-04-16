
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('dashboard/', include('admin_dashboard.urls', namespace='admin_dashboard')),
    path('cart/', include('cart.urls', namespace='cart')),
    path('checkout/', include('checkout.urls', namespace='checkout')),
    path('', include('home.urls', namespace='home')),  # homepage at root
    path('orders/', include('orders.urls', namespace='orders')),
    path('payments/', include('payments.urls', namespace='payments')),
    path('products/', include('products.urls', namespace='products')),
    path('reviews/', include('reviews.urls', namespace='reviews')),
    path('search/', include('search.urls', namespace='search')),
]
