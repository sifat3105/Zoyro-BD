import json
from django.shortcuts import render
from django.contrib.auth import get_backends
from django.contrib.auth import logout, authenticate, login
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.utils import timezone
import random
import string

GOOGLE_CLIENT_ID = "321987152556-sfp8useco7j0t261q8mkj9u88ih23j52.apps.googleusercontent.com"

@csrf_exempt
def onetap_login(request):
    if request.method == "POST":
        data = json.loads(request.body)
        token = data.get("credential")

        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
            email = idinfo['email']
            name = idinfo.get('name', '')

            # Get or create user
            user, created = User.objects.get_or_create(username=email, defaults={"email": email, "first_name": name})
            login(request, user)
            return JsonResponse({"status": "ok"})

        except ValueError:
            return JsonResponse({"status": "error", "message": "Invalid token"}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid method"}, status=405)


def logout_view(request):
    logout(request)
    return redirect('home:home')

# reverse('products:detail', args=[product.id])

def login_view(request):
    if request.method == 'post':
        email = request.POST.get('email')
        password = request.POST.get('password')
        username = email.split('@')[0]
        user = authenticate(request, user)
    pass

def register_view(request):
    pass


def create_guest_user(request):
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    username = f"guest_user{timestamp}{random_str}"

    user = User.objects.create_user(username=username, password='guestpassword')

    # Automatically assign first backend
    backend = get_backends()[0]
    login(request, user, backend=f"{backend.__module__}.{backend.__class__.__name__}")
    
    return username


def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('home:home')
    if request.user.username.startswith('guest_user'):
        return redirect('home:home')
    return render(request, 'account/profile.html',{
        'user':request.user,
    })