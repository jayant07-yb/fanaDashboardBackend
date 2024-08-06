# Create your views here.
from django.shortcuts import render
from .models import TableActivity, UserActivity
from django.contrib.auth.decorators import login_required
import json

@login_required
def table_activity_view(request):
    activities = TableActivity.objects.all().order_by('timestamp')
    data = [{
        'timestamp': activity.timestamp.isoformat(),
        'is_active': 1 if activity.is_active else 0
    } for activity in activities]
    return render(request, 'fanaInsight/table_activity.html', {'activities': json.dumps(data)})

@login_required
def user_activity_view(request):
    activities = UserActivity.objects.all().order_by('timestamp')
    data = [{
        'timestamp': activity.timestamp.isoformat(),
        'is_active': 1 if activity.is_active else 0
    } for activity in activities]
    print("User activity data: ", data)
    return render(request, 'fanaInsight/user_activity.html', {'activities': json.dumps(data)})
