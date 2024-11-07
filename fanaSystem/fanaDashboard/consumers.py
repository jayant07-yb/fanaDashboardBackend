from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import DenyConnection
import json

class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Check if the user is authenticated
        if self.scope['user'].is_anonymous:
            # Deny the connection if the user is not authenticated
            raise DenyConnection("User is not authenticated.")
        
        # Add the user to the "dashboard_group" if authenticated
        await self.channel_layer.group_add("dashboard_group", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Remove the user from the "dashboard_group" on disconnect
        await self.channel_layer.group_discard("dashboard_group", self.channel_name)

    async def receive(self, text_data):
        # Handle messages received from the WebSocket client if needed
        data = json.loads(text_data)
        table_id = data.get("table_id")
        state = data.get("state")

        # You can process data here or send it to the group
        await self.channel_layer.group_send(
            "dashboard_group",
            {
                "type": "broadcast_message",
                "table_id": table_id,
                "state": state,
            }
        )

    async def broadcast_message(self, event):
        # Send a message to WebSocket clients in the group
        await self.send(text_data=json.dumps({
            "table_id": event["table_id"],
            "state": event["state"]
        }))
