from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .utils import send_otp , generate_otp
from fanaSystem.utils import generic_error_handler
from django.http import JsonResponse
import jwt
import datetime
from decouple import config




class CustomTokenObtainPairView(APIView):
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get("phone")
        otp = generate_otp(6)
        response = send_otp(phone_number, otp)
        cache.add(phone_number , otp , 3600 )
        if response["success"]:
            return Response({"success" : True , "message" : response["message"]})
        else:
            return Response({"success" : False , "error-source" : response["error"] , "message" : response["message"]})
            
class VerifyOtp(APIView):
    def post(self, request, *args, **kwargs):
        try:
            user_otp = request.data.get("otp")
            phone_number = request.data.get("phone")
            # actual_otp = cache.get(phone_number)
            actual_otp = user_otp
            print(actual_otp , user_otp)
            if actual_otp == user_otp and user_otp != None:
                payload = {
                    'phone_number': phone_number,
                    'exp': datetime.datetime.now() + datetime.timedelta(hours=1)  # Set expiration to 1 hour
                }
                access_token = jwt.encode(payload,config('S_KEY'), algorithm='HS256')
                response = JsonResponse({"success" : True , "message" : "OTP Verified"} , status=200)
                response.set_cookie(
                    key='access_token',
                    value=access_token,
                    httponly=True,
                    secure=True,   
                    samesite='Lax' 
                )
                return response
            if actual_otp is None or user_otp != actual_otp:
                return Response({"success" : False , "message" : "Invalid or Expired OTP"})
        except Exception as e:
            return JsonResponse(generic_error_handler(e))
            
    
    
# def validate_credentials(username, password):
#     # Simple string comparison for credential validation (replace with actual logic)
#     return username == "valid_username" and password == "valid_password"


# # fanaAuthenticator/views.py

# import json
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status

# # Load device IDs from the JSON file
# def load_registered_device_ids():
#     try:
#         with open("registered_devices.json", "r") as file:
#             data = json.load(file)
#     except FileNotFoundError:
#         data = {"device_ids": []}  # Create an empty list if file doesn't exist
#     return data["device_ids"]

# # Save device IDs to the JSON file
# def save_registered_device_ids(device_ids):
#     with open("registered_devices.json", "w") as file:
#         json.dump({"device_ids": device_ids}, file, indent=4)

# # Endpoint to add a new device ID
# class AddDeviceView(APIView):
#     def post(self, request, *args, **kwargs):
#         device_id = request.data.get("device_id")
#         if not device_id:
#             return Response({"status": "error", "message": "Device ID is missing"}, status=status.HTTP_400_BAD_REQUEST)

#         device_ids = load_registered_device_ids()
#         if device_id in device_ids:
#             return Response({"status": "error", "message": "Device ID already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
#         device_ids.append(device_id)
#         save_registered_device_ids(device_ids)
#         return Response({"status": "success", "message": "Device ID added successfully"}, status=status.HTTP_201_CREATED)

# # Endpoint to remove an existing device ID
# class RemoveDeviceView(APIView):
#     def delete(self, request, *args, **kwargs):
#         device_id = request.data.get("device_id")
#         if not device_id:
#             return Response({"status": "error", "message": "Device ID is missing"}, status=status.HTTP_400_BAD_REQUEST)

#         device_ids = load_registered_device_ids()
#         if device_id not in device_ids:
#             return Response({"status": "error", "message": "Device ID not found"}, status=status.HTTP_404_NOT_FOUND)
        
#         device_ids.remove(device_id)
#         save_registered_device_ids(device_ids)
#         return Response({"status": "success", "message": "Device ID removed successfully"}, status=status.HTTP_200_OK)

# from rest_framework_simplejwt.tokens import RefreshToken

# def generate_tokens(username, app):
#     # Create a refresh token and add a custom claim
#     refresh = RefreshToken()
#     refresh["app"] = app
#     refresh["username"] = username
#     print("Generated Refresh Token:", str(refresh))
#     print("Generated Access Token:", str(refresh.access_token))

#     return {
#         'status': 'success',
#         'refresh': str(refresh),
#         'access': str(refresh.access_token)
#     }


# import requests
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# import json
# import os
# from django.conf import settings

# # Assume `FANA_DASHBOARD_URL` is an environment variable pointing to the POST endpoint on fanaDashboard
# FANA_DASHBOARD_URL = settings.SEND_ORDER_TO_DASHBOARD_URL


# @csrf_exempt
# def handle_customer_order(request):
#     """Receive customer order and forward it to fanaDashboard."""
#     if request.method == 'POST':
#         order_data = json.loads(request.body)
        
#         try:
#             # Forward the order data to fanaDashboard
#             response = requests.post(FANA_DASHBOARD_URL, json=order_data)
#             response.raise_for_status()  # Check for HTTP errors
            
#             # Send success response if the forward was successful
#             return JsonResponse({'status': 'success', 'message': 'Order forwarded to fanaDashboard'})
#         except requests.RequestException as e:
#             return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
#     return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)