from django.urls import resolve, reverse
from django.http import JsonResponse
from .utils import generic_error_handler
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from decouple import config
import jwt
from django.utils.deprecation import MiddlewareMixin
from .error_handler import ErrorHandler



class ErrorHandlingMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        """
        This method is called when an exception is raised in the view.
        It uses the ErrorHandler to return an appropriate response.
        """
        return ErrorHandler.handle_error(exception)



from django.urls import resolve
from django.http import JsonResponse
from decouple import config
import jwt
from .error_handler import ErrorHandler

class RouteSpecificMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Define the allowed named routes
        self.allowed_routes = [
            'fanaAuthenticator:protected_route_check',
        ]

    def __call__(self, request):
        try:
            match = resolve(request.path)
            print(f"{match.app_name}:{match.url_name}")
            
            if f"{match.app_name}:{match.url_name}" in self.allowed_routes:
                print(f"Middleware activated for {request.path}")
                jwt_token = request.COOKIES.get('access_token')
                print(jwt_token)

                if not jwt_token or jwt_token is None:
                    raise jwt.DecodeError("Session Expired, Please Login")

                try:
                    decoded_token = jwt.decode(jwt_token, config("S_KEY"), algorithms=["HS256"])
                    request.user_data = decoded_token['phone_number']
                    print(f"Token is valid: {decoded_token}")
                except Exception as e:
                    raise e
        except Exception as e:
            return ErrorHandler.handle_error(e)

        response = self.get_response(request)
        return response


