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
