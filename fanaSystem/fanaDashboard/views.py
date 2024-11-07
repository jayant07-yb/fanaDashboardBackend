from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from django.conf import settings

logging.basicConfig(filename='table_activity.log', level=logging.INFO, format='%(asctime)s - %(message)s')

@csrf_exempt
def handle_fana_call(request):
    """Handle requests from the ESP8266 device and broadcast via WebSocket."""
    if request.method == 'POST':
        data = json.loads(request.body)
        table_id = data.get('table_id')
        state = data.get('state')
        time_taken = data.get('time_taken')
        log_message = f"Table ID: {table_id}, State: {state}, Time Taken: {time_taken} ms"
        print(log_message)
        logging.info(log_message)
        
        if table_id and state:
            # Get the channel layer for broadcasting
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "dashboard_group",  # Group name that the consumer listens to
                {
                    "type": "broadcast_message",
                    "table_id": table_id,
                    "state": state
                }
            )
            return JsonResponse({'status': 'success', 'message': 'Data broadcasted to WebSocket clients'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@login_required(login_url='/fanaDashboard/login/')
def dashboard(request):
    """Render the dashboard page."""
    return render(request, 'dashboard.html')


def login_view(request):
    app_id = request.session.get("app_id", "YOUR_APP_ID")  # Use session or default App ID
    auth_server_login_url = settings.AUTH_SERVER_LOGIN_URL  # Get URL from settings
    return render(request, 'login.html', {"app_id": app_id, "auth_server_login_url": auth_server_login_url})

import jwt
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def set_session(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        token = data.get('jwt')

        if not token:
            return JsonResponse({'status': 'error', 'message': 'JWT token is required'}, status=400)

        try:
            print(f"Decodign the json object wrt {settings.SECRET_KEY}", )
            # Decode JWT using the shared secret key
            decoded_data = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            username = decoded_data.get('username')

            print (f"Decoded the obj {decoded_data}, {username}")
            # Set session with username
            request.session['username'] = username
            request.session['jwt'] = token  # Optionally store the JWT itself

            # Optionally create a User object if not exists, or mark the user as authenticated
            user, created = User.objects.get_or_create(username=username)
            login(request, user)  # Marks user as authenticated in the session

            return JsonResponse({'status': 'success', 'message': 'Session set successfully'})
        except jwt.ExpiredSignatureError:
            return JsonResponse({'status': 'error', 'message': 'Token expired'}, status=400)
        except jwt.InvalidTokenError:
            return JsonResponse({'status': 'error', 'message': 'Invalid token'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
