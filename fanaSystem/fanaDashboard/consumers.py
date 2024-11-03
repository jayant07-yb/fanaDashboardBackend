# your_app_name/consumers.py

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json

class DashboardConsumer(WebsocketConsumer):
    def connect(self):
        # Join a group to broadcast messages to all connected clients
        async_to_sync(self.channel_layer.group_add)(
            "dashboard_group",
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave the group when WebSocket disconnects
        async_to_sync(self.channel_layer.group_discard)(
            "dashboard_group",
            self.channel_name
        )

    def broadcast_message(self, event):
        # Send message to WebSocket client
        self.send(text_data=json.dumps({
            'table_id': event['table_id'],
            'state': event['state']
        }))
