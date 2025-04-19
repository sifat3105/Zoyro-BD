from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('details/<slug:product_slug>/', views.product_details, name='details'),
]
