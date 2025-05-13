from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    path('search/products/', views.js_search_products, name='js_search_products'),
    path('search/', views.search_redirect, name='search_redirect'),
    path('catalog/', views.product_search, name='product_search'),
]
