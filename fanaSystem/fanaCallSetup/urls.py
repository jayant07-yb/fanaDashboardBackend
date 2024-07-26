from django.urls import path
from . import views

urlpatterns = [
    path('fanaCallSetup/', views.fana_call_setup_view, name='fanaCallSetup'),
]
