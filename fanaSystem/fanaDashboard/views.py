from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from fanaCallSetup.models import FanaCallRequest
from django.shortcuts import render, redirect
from fanaCallSetup.models import FanaCallRequest
from django.http import JsonResponse
import json
import logging

# Configure logging to output to a file
logging.basicConfig(filename='table_activity.log', level=logging.INFO, format='%(asctime)s - %(message)s')


global data_changed
data_changed = False

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # user = form.get_user()
            # # login(request, user)
            return redirect('fanaDashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'fanaDashboard/login.html', {'form': form})

@csrf_exempt
def handle_fana_call(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        table_id = data.get('table_id')
        state = data.get('state')
        time_taken = data.get('time_taken')

        if table_id and state and time_taken is not None:
            # Format the log entry
            log_message = f"Table ID: {table_id}, State: {state}, Time Taken: {time_taken} ms"
            print(log_message)
            
            # Log the event to a file and print to console
            logging.info(log_message)

            return JsonResponse({'status': 'success', 'message': 'Request logged successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

# TODO use jwt tocken to login 
#
@csrf_exempt
@login_required
def dashboard_view(request):
    global data_changed
    if request.method == 'POST':
        button_type = request.POST.get('button_type')
        table_id = request.POST.get('table_id')
        request_to_handle = FanaCallRequest.objects.get(table_id=table_id)

        if button_type == 'call_waiter':
            request_to_handle.call_waiter_state = 'in_progress'
        elif button_type == 'bring_bill':
            request_to_handle.bring_bill_state = 'in_progress'
        elif button_type == 'order':
            request_to_handle.order_state = 'in_progress'
        elif button_type == 'bring_water':
            request_to_handle.bring_water_state = 'in_progress'

        request_to_handle.handled_by = request.user
        request_to_handle.save()
        data_changed = True


        return redirect('fanaDashboard')

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

    tables = {table_id: requests for table_id, requests in tables.items() if requests}

    return render(request, 'fanaDashboard/dashboard.html', {'tables': tables})
