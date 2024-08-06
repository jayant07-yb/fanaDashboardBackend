from django.urls import path
from . import views

urlpatterns = [
    path('tables/', views.table_activity_view, name='table_activity'),
    path('users/', views.user_activity_view, name='user_activity'),
]