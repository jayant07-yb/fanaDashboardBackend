from django.shortcuts import render, redirect
from fanaCallSetup.models import FanaCallRequest

def dashboard_view(request):
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        request_to_handle = FanaCallRequest.objects.get(id=request_id)
        request_to_handle.handled = True
        request_to_handle.save()
        return redirect('fanaDashboard')

    requests = FanaCallRequest.objects.filter(handled=False).order_by('-timestamp')
    return render(request, 'fanaDashboard/dashboard.html', {'requests': requests})
