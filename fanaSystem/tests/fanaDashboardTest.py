import json
import requests
import time
import asyncio
from threading import Event
import common as settings
import websockets

BASE_URL = settings.BASE_URL
WS_URL = settings.WSL_SERVER_URL

USERNAME = "valid_username"
PASSWORD = "valid_password"
ORDER_ID = "order_123"
DEVICE_ID = "device_123"
TABLE_ID = "table_1"

access_token = None
order_reflected = False
fana_call_reflected = False
ws = None
stop_event = Event()
ws_ready_event = Event()  # This event will be used to signal when the WebSocket is ready

# Function to get JWT token
def get_jwt_token():
    global access_token
    print("[INFO] Getting JWT token...")
    response = requests.post(
        f"{BASE_URL}/fanaAuthenticator/api/token/",
        json={"username": USERNAME, "password": PASSWORD},
    )
    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens.get("access")
        print("[INFO] JWT Token acquired:", tokens)
        return tokens
    else:
        print("[ERROR] Failed to acquire JWT token:", response.json())
        return None


# Function to connect to WebSocket
async def connect_websocket(token):
    global ws
    try:
        headers = {
            "Authorization": f"Bearer {token}"
        }
        async with websockets.connect(WS_URL, additional_headers=headers) as websocket:
            print(f"Connected to WebSocket at {WS_URL}")
            ws = websocket

            # Signal that the WebSocket is ready
            ws_ready_event.set()

            # Listen for messages
            while True:
                try:
                    result = await websocket.recv()
                    print(f"Received WebSocket message: {result}")
                    # You can process the result as per your need
                except websockets.exceptions.ConnectionClosed:
                    print("[INFO] WebSocket connection closed.")
                    break

    except Exception as e:
        print(f"[ERROR] Failed to connect to WebSocket: {e}")

# Send Order function
def send_order():
    global access_token
    print("[INFO] Sending order...")
    response = requests.post(
        f"{BASE_URL}/fanaDashboard/receiveOrder/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "order_id": ORDER_ID,
            "order_details": {
                "items": [
                    {"name": "Burger", "cost": 100, "quantity": 2, "itemTotal": 200},
                    {"name": "Fries", "cost": 50, "quantity": 1, "itemTotal": 50},
                ],
                "totalAmount": 250,
            },
        },
    )
    print("[INFO] Send Order Response:", response.json())
    return response.status_code == 200 and response.json().get("status") == "success"

# Handle Fana Call function
def handle_fana_call():
    global access_token
    print("[INFO] Sending fana call...")
    response = requests.post(
        f"{BASE_URL}/fanaDashboard/handleFanaCall/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"table_id": TABLE_ID, "state": "calling", "time_taken": 1000},
    )
    print("[INFO] Handle Fana Call Response:", response.json())
    return response.status_code == 200 and response.json().get("status") == "success"

# Main test function
async def test_sequence():
    global order_reflected, fana_call_reflected, ws, stop_event

    # Step 1: Get JWT Token
    tokens = get_jwt_token()
    if not tokens:
        print("[ERROR] Test failed: Unable to acquire JWT token.")
        print("Result: FAILED")
        return

    try:
        # Step 2: Connect to WebSocket asynchronously
        print("[INFO] Connecting to WebSocket...")
        # The WebSocket connection will be established in the background
        asyncio.create_task(connect_websocket(access_token))

        # Wait for the WebSocket to be ready before proceeding
        print("[INFO] Waiting for WebSocket connection to be ready...")
        await asyncio.wait_for(ws_ready_event.wait(), timeout=30)  # Wait for WebSocket to be ready or timeout after 30 seconds
        print("[INFO] WebSocket is ready. Proceeding...")

        # Step 3: Send Order
        if not send_order():
            print("[ERROR] Test failed: Order not sent successfully.")
            stop_event.set()
            print("Result: FAILED")
            return

        time.sleep(2)  # Allow some time for the dashboard to process

        # Step 4: Send Fana Call
        if not handle_fana_call():
            print("[ERROR] Test failed: Fana call not sent successfully.")
            stop_event.set()
            print("Result: FAILED")
            return

        time.sleep(2)  # Allow some time for WebSocket events to be received

        # Step 5: Validate WebSocket Events
        print("[INFO] Verifying WebSocket events...")
        if not order_reflected:
            print("[ERROR] Order not reflected on dashboard.")
        if not fana_call_reflected:
            print("[ERROR] Fana call not reflected on dashboard.")

        # Final Test Result
        if order_reflected and fana_call_reflected:
            print("Result: PASSED")
        else:
            print("Result: FAILED")

    except Exception as e:
        print(f"[ERROR] Test failed with exception: {e}")
        print("Result: FAILED")
    finally:
        # Stop the WebSocket listener
        stop_event.set()
        if ws:
            await ws.close()

# Run the Test
if __name__ == "__main__":
    asyncio.run(test_sequence())
