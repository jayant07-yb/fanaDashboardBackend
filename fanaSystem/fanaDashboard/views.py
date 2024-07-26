from django.shortcuts import render
from fanaCallSetup.models import FanaCallRequest

def dashboard_view(request):
    requests = FanaCallRequest.objects.all().order_by('-timestamp')
    return render(request, 'fanaDashboard/dashboard.html', {'requests': requests})
