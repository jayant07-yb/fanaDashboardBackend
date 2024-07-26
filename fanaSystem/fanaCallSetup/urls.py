from django.urls import path
from . import views

urlpatterns = [
    path('setup/', views.fana_call_setup_view, name='fanaCallSetup'),
    path('handleFanaCall/', views.handle_fana_call, name='handleFanaCall'),
]
