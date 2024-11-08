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

        table_id = data.get("table_id", None)
        state = data.get("state", None)
        message_type = data.get("message_type", None)
        order_id = data.get("order_id", None)
        order_details = data.get("order_details", "")
        time_taken = data.get("time_taken", 0)

        # Send the processed data to the group
        await self.channel_layer.group_send(
            "dashboard_group",
            {
                "type": "broadcast_message",
                "message_type": message_type,
                "order_id": order_id,
                "order_details": order_details,
                "table_id": table_id,
                "state": state,
                "time_taken": time_taken,
            }
        )

    async def broadcast_message(self, event):
        # Send a message to WebSocket clients in the group with default values if fields are missing
        await self.send(text_data=json.dumps({
            "message_type": event.get("message_type", None),
            "order_id": event.get("order_id", None),
            "order_details": event.get("order_details", ""),
            "table_id": event.get("table_id", None),
            "state": event.get("state", None),
            "time_taken": event.get("time_taken", 0)
        }))

