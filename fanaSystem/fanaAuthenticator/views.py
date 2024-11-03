from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

class CustomTokenObtainPairView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        app = request.data.get("app")  # Get the app identifier from the request

        # Validate credentials (replace with actual validation logic as needed)
        if validate_credentials(username, password):
            print("Credentials validated successfully.")

            # Generate JWT token with an additional claim for the app
            refresh = RefreshToken()
            refresh["app"] = app  # Add custom claim for app

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        else:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

def validate_credentials(username, password):
    # Simple string comparison for credential validation (replace with actual logic)
    return username == "valid_username" and password == "valid_password"


# fanaAuthenticator/views.py

import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Load device IDs from the JSON file
def load_registered_device_ids():
    try:
        with open("registered_devices.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {"device_ids": []}  # Create an empty list if file doesn't exist
    return data["device_ids"]

# Save device IDs to the JSON file
def save_registered_device_ids(device_ids):
    with open("registered_devices.json", "w") as file:
        json.dump({"device_ids": device_ids}, file, indent=4)

# Endpoint to add a new device ID
class AddDeviceView(APIView):
    def post(self, request, *args, **kwargs):
        device_id = request.data.get("device_id")
        if not device_id:
            return Response({"status": "error", "message": "Device ID is missing"}, status=status.HTTP_400_BAD_REQUEST)

        device_ids = load_registered_device_ids()
        if device_id in device_ids:
            return Response({"status": "error", "message": "Device ID already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        device_ids.append(device_id)
        save_registered_device_ids(device_ids)
        return Response({"status": "success", "message": "Device ID added successfully"}, status=status.HTTP_201_CREATED)

# Endpoint to remove an existing device ID
class RemoveDeviceView(APIView):
    def delete(self, request, *args, **kwargs):
        device_id = request.data.get("device_id")
        if not device_id:
            return Response({"status": "error", "message": "Device ID is missing"}, status=status.HTTP_400_BAD_REQUEST)

        device_ids = load_registered_device_ids()
        if device_id not in device_ids:
            return Response({"status": "error", "message": "Device ID not found"}, status=status.HTTP_404_NOT_FOUND)
        
        device_ids.remove(device_id)
        save_registered_device_ids(device_ids)
        return Response({"status": "success", "message": "Device ID removed successfully"}, status=status.HTTP_200_OK)

