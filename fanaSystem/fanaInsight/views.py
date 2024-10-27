# Create your views here.
from django.shortcuts import render
from .models import TableActivity, UserActivity
from django.contrib.auth.decorators import login_required
import json
from django.contrib.auth.models import User

@login_required
def table_activity_view(request):
    table_activities = []
    tables = TableActivity.objects.values_list('table_id', flat=True).distinct()
    for table_id in tables:
        activities = TableActivity.objects.filter(table_id=table_id).order_by('timestamp')
        data = [{
            'timestamp': activity.timestamp.isoformat(),
            'is_active': 1 if activity.is_active else 0
        } for activity in activities]
        table_activities.append({"timeseries": json.dumps(data), "table": table_id})
    return render(request, 'fanaInsight/table_activity.html', {'activities': table_activities})

@login_required
def user_activity_view(request):
    user_activities = []
    users = User.objects.all()
    for user in users:
        activities = UserActivity.objects.filter(user=user).order_by('timestamp')
        data = [{
            'timestamp': activity.timestamp.isoformat(),
            'is_active': 1 if activity.is_active else 0
        } for activity in activities]
        
        # Calculate additional details
        max_active_time = calculate_max_active_time(activities)
        average_active_time = calculate_average_active_time(activities)
        num_servers = calculate_num_servers(activities)
        
        user_activities.append({
            "timeseries": json.dumps(data),
            "user": user.username,
            "maxActiveTime": max_active_time,
            "averageActiveTime": average_active_time,
            "numServers": num_servers
        })
    return render(request, 'fanaInsight/user_activity.html', {'activities': user_activities})

def calculate_max_active_time(activities):
    # Implement logic to calculate max active time
    return 1

def calculate_average_active_time(activities):
    # Implement logic to calculate average active time
    return 2

def calculate_num_servers(activities):
    # Implement logic to calculate number of servers
    return 3
