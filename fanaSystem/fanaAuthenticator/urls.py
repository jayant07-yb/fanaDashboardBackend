# fanaAuthenticator/urls.py

from django.urls import path
from .views import CustomTokenObtainPairView, VerifyOtp

# urlpatterns = [
#     path('api/token/', CustomTokenObtainPairView.as_view(), name='custom_token_obtain_pair'),
#     path('api/add_device/', AddDeviceView.as_view(), name='add_device'),
#     path('api/remove_device/', RemoveDeviceView.as_view(), name='remove_device'),
#     path('handle_customer_order/', handle_customer_order, name='handle_customer_order')
# ]
urlpatterns = [
    path('api/send-otp', CustomTokenObtainPairView.as_view(), name='custom_token_obtain_pair'),
    path('api/verify-otp', VerifyOtp.as_view(), name='verify-otp'),

]
