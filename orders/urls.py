from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cod/create/<int:quantity>/<str:size>/<slug:product_slug>/<int:address_id>/', views.cod_create, name='cod_create'),
    path('cod/create/<int:address_id>/', views.cod_create2, name='cod_create2'),
    path('confirmed/<str:order_number>/', views.order_confirmed, name='order_confirmed'),
    path('details/', views.order_detail, name='details'),
]
