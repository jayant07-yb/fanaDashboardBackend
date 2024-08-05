from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .forms import SetupForm
from .models import FanaCallRequest
import json
import subprocess
import os
import time
import socket
from tqdm import tqdm
import serial.tools.list_ports

def get_com_ports():
    ports = serial.tools.list_ports.comports()
    return [(port.device, f"{port.device} - {port.description}") for port in ports]

def get_server_ip():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

def generate_esp32_code(wifi_name, wifi_password, table_id):
    server_ip = get_server_ip()
    server_url = f"http://{server_ip}:8000/fanaCall/handleFanaCall/"
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'fanaCallSetup', 'esp32_code_template.cpp')
    with open(template_path, 'r') as template_file:
        code = template_file.read()
    code = code.replace('{wifi_name}', wifi_name)
    code = code.replace('{wifi_password}', wifi_password)
    code = code.replace('{server_url}', server_url)
    code = code.replace('{table_id}', table_id)
    return code

def fana_call_setup_view(request):
    com_ports = get_com_ports()
    if request.method == 'POST':
        form = SetupForm(request.POST)
        if form.is_valid():
            table_id = form.cleaned_data['table_id']
            wifi_name = form.cleaned_data['wifi_name']
            wifi_password = form.cleaned_data['wifi_password']
            port = form.cleaned_data['port']

            code = generate_esp32_code(wifi_name, wifi_password, table_id)

            src_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
            if not os.path.exists(src_dir):
                os.makedirs(src_dir)
            with open(os.path.join(src_dir, 'main.cpp'), 'w') as f:
                f.write(code)

            try:
                pio_project_dir = os.path.join(os.path.dirname(__file__), '..')

                env = os.environ.copy()
                env['PLATFORMIO_UPLOAD_PORT'] = port
                result = subprocess.run(
                    ['platformio', 'run', '-t', 'upload'],
                    cwd=pio_project_dir,
                    check=True,
                    env=env,
                    capture_output=True
                )

                response = {
                    'status': 'success',
                    'output': result.stdout.decode(),
                    'message': f'Success message for table {table_id}'
                }
            except subprocess.CalledProcessError as e:
                print("Got error: ")
                print(e.stderr.decode())

                response = {
                    'status': 'error',
                    'message': e.stderr.decode()
                }
            return JsonResponse(response)
    else:
        form = SetupForm()
    return render(request, 'fanaCallSetup/setup.html', {'form': form, 'com_ports': com_ports})



@csrf_exempt
def handle_fana_call(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        combined_state = data.get('combined_state')
        table_id = data.get('table_id')

        if combined_state and table_id:
            # Retrieve or create the FanaCallRequest object
            table_request, created = FanaCallRequest.objects.get_or_create(table_id=table_id)

            # Update the corresponding states based on the combined state
            table_request.call_waiter_state = 'pressed' if combined_state[0] == '1' else 'released'
            table_request.bring_bill_state = 'pressed' if combined_state[1] == '1' else 'released'
            table_request.order_state = 'pressed' if combined_state[2] == '1' else 'released'
            table_request.bring_water_state = 'pressed' if combined_state[3] == '1' else 'released'

            table_request.timestamp = timezone.now()
            table_request.save()

            return JsonResponse({'status': 'success', 'message': 'Request logged successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)