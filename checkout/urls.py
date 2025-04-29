from django.urls import path
from . import views

app_name = 'checkout'

urlpatterns = [
    path('', views.checkout_view, name='checkout_view'),
    path('<slug:product_slug>/<int:quantity>/<str:size>/', views.direct_checkout, name='direct_checkout'),
]
