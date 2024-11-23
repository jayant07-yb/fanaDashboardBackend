from django.http import JsonResponse
from django.core.exceptions import ValidationError, PermissionDenied
import jwt

class ErrorHandler:
    @staticmethod
    def handle_error(exception):
        """
        A method to handle errors and return a proper JsonResponse.
        """
        print("Exception data" , exception)
        if isinstance(exception, ValidationError):
            return JsonResponse({
                "error": "Validation error",
                "message": str(exception)
            }, status=400)
        
        elif isinstance(exception, PermissionDenied):
            return JsonResponse({
                "error": "Permission denied",
                "message": str(exception)
            }, status=403)
        
        # Handle custom JWT error
        elif isinstance(exception, jwt.ExpiredSignatureError):
            return JsonResponse({
                "error": "JWT error",
                "message": "Token has expired"
            }, status=401)
        
        elif isinstance(exception, jwt.DecodeError):
            return JsonResponse({
                "error": "JWT error",
                "message": str(exception)
            }, status=401)
        
        # Handle any other custom errors
        elif isinstance(exception, Exception):
            return JsonResponse({
                "error": "Internal Server Error",
                "message": str(exception)
            }, status=500)
        
        # Default case: return generic 500 error
        return JsonResponse({
            "error": "Unknown error",
            "message": "An unknown error occurred"
        }, status=500)
