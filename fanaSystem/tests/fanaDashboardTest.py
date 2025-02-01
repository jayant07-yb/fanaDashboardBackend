import json
import requests
import time
import websockets
import common as settings

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


# Function to connect to WebSocket (Synchronous)
def connect_websocket(token):
    global ws
    try:
        headers = {
            "Authorization": f"Bearer {token}"
        }

        # Debugging: Print the URL and headers being used
        print(f"Connecting to WebSocket at {WS_URL} with headers {headers}")

        # Synchronously connect to the WebSocket
        ws = websockets.connect(WS_URL, extra_headers=headers)
        
        # Wait for the connection to be established
        connection = ws.__enter__()

        print(f"Connected to WebSocket at {WS_URL}")
        return connection

    except Exception as e:
        print(f"[ERROR] Failed to connect to WebSocket: {e}")
        return None

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
def test_sequence():
    global order_reflected, fana_call_reflected, ws

    # Step 1: Get JWT Token
    tokens = get_jwt_token()
    if not tokens:
        print("[ERROR] Test failed: Unable to acquire JWT token.")
        print("Result: FAILED")
        return

    try:
        # Step 2: Connect to WebSocket synchronously
        print("[INFO] Connecting to WebSocket...")
        connection = connect_websocket(access_token)

        if not connection:
            print("[ERROR] Test failed: WebSocket connection not established.")
            print("Result: FAILED")
            return

        # Step 3: Send Order
        if not send_order():
            print("[ERROR] Test failed: Order not sent successfully.")
            print("Result: FAILED")
            return

        time.sleep(2)  # Allow some time for the dashboard to process

        # Step 4: Send Fana Call
        if not handle_fana_call():
            print("[ERROR] Test failed: Fana call not sent successfully.")
            print("Result: FAILED")
            return

        time.sleep(2)  # Allow some time for WebSocket events to be received

        # Final Test Result
        print("Result: PASSED")

    except Exception as e:
        print(f"[ERROR] Test failed with exception: {e}")
        print("Result: FAILED")
    finally:
        # Close the WebSocket connection
        if ws:
            ws.close()
            print("[INFO] WebSocket connection closed.")

# Run the Test
if __name__ == "__main__":
    test_sequence()
