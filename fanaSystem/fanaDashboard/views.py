# your_app_name/views.py

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import logging

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

def dashboard(request):
    """Render the dashboard page."""
    return render(request, 'dashboard.html')


def login_view(request):
    # Set app_id in the session if it’s not already there
    if "app_id" not in request.session:
        request.session["app_id"] = "YOUR_APP_ID"  # Replace "YOUR_APP_ID" with the actual App ID or dynamic logic

    # Retrieve app_id from session
    app_id = request.session.get("app_id")

    # Render the login form with the app_id context
    return render(request, 'login.html', {"app_id": app_id})