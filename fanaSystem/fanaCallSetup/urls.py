from django.urls import path
from . import views

urlpatterns = [
    path('', views.fana_call_setup_view, name='fanaCallSetup'),
]
