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
        user_activities.append({"timeseries": json.dumps(data), "user": user.username})
    return render(request, 'fanaInsight/user_activity.html', {'activities': user_activities})

