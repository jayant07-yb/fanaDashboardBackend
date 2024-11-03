# your_app_name/routing.py

from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/dashboard/', consumers.DashboardConsumer.as_asgi()),  # Define WebSocket route
]
