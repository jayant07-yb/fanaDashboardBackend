import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
import threading
import time
from fanaCallSetup.models import FanaCallRequest

data_changed = False

class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'dashboard_updates'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        # Start a background thread for polling
        self.polling_thread = threading.Thread(target=self.poll_for_changes)
        self.polling_thread.start()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

        # Stop the polling thread
        self.polling_thread.do_run = False

    def poll_for_changes(self):
        t = threading.currentThread()
        global data_changed
        while getattr(t, "do_run", True):
            time.sleep(2)  # Polling interval

            # Check for changes in the state
            if data_changed:
                async_to_sync(self.channel_layer.group_send)(
                    self.group_name,
                    {
                        'type': 'send_update',
                        'text': self.get_updated_data()
                    }
                )
                data_changed = False

    def get_updated_data(self):
        # Fetch the current state of all requests
        requests = FanaCallRequest.objects.all()
        data = {
            "requests": [
                {
                    "table_id": request.table_id,
                    "call_waiter_state": request.call_waiter_state,
                    "bring_bill_state": request.bring_bill_state,
                    "order_state": request.order_state,
                    "bring_water_state": request.bring_water_state,
                } for request in requests
            ]
        }
        return data

    async def send_update(self, event):
        await self.send(text_data=json.dumps(event["text"]))
