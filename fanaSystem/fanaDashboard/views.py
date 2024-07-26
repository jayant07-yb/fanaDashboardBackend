from django.shortcuts import render, redirect
from fanaCallSetup.models import FanaCallRequest
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

@csrf_exempt
def dashboard_view(request):
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        button_type = request.POST.get('button_type')
        table_id = request.POST.get('table_id')
        request_to_handle = FanaCallRequest.objects.get(table_id=table_id)

        # Update the corresponding state based on the button type
        if button_type == 'call_waiter':
            request_to_handle.call_waiter_state = 'in_progress'
        elif button_type == 'bring_bill':
            request_to_handle.bring_bill_state = 'in_progress'
        elif button_type == 'order':
            request_to_handle.order_state = 'in_progress'
        elif button_type == 'bring_water':
            request_to_handle.bring_water_state = 'in_progress'

        request_to_handle.save()
        return redirect(reverse('fanaDashboard'))

    # Aggregate the active requests for each table
    requests = FanaCallRequest.objects.filter(
        call_waiter_state='pressed') | FanaCallRequest.objects.filter(
        bring_bill_state='pressed') | FanaCallRequest.objects.filter(
        order_state='pressed') | FanaCallRequest.objects.filter(
        bring_water_state='pressed')

    tables = {}
    for table_request in requests:
        if table_request.table_id not in tables:
            tables[table_request.table_id] = []
        if table_request.call_waiter_state == 'pressed':
            tables[table_request.table_id].append('Call Waiter')
        if table_request.bring_bill_state == 'pressed':
            tables[table_request.table_id].append('Bring Bill')
        if table_request.order_state == 'pressed':
            tables[table_request.table_id].append('Order')
        if table_request.bring_water_state == 'pressed':
            tables[table_request.table_id].append('Bring Water')

    # Filter out tables with no active requests
    tables = {table_id: requests for table_id, requests in tables.items() if requests}

    return render(request, 'fanaDashboard/dashboard.html', {'tables': tables})
