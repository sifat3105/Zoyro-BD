from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path("onetap-login/", views.onetap_login, name="onetap_login"),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
]


