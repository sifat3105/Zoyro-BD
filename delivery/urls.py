from django.urls import path
from . import views

app_name = 'delivery'

urlpatterns = [
    path('address-create/', views.create_delivery_address_view, name='create_delivery_address')
]
