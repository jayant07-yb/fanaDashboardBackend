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
from tqdm import tqdm
import serial.tools.list_ports

def get_com_ports():
    ports = serial.tools.list_ports.comports()
    return [(port.device, f"{port.device} - {port.description}") for port in ports]

def generate_esp32_code(wifi_name, wifi_password, server_url, table_id):
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

            server_url = request.build_absolute_uri('/fanaCall/handleFanaCall/')  # Dynamically get the server URL

            code = generate_esp32_code(wifi_name, wifi_password, server_url, table_id)

            src_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
            if not os.path.exists(src_dir):
                os.makedirs(src_dir)
            with open(os.path.join(src_dir, 'main.cpp'), 'w') as f:
                f.write(code)

            try:
                pio_project_dir = os.path.join(os.path.dirname(__file__), '..')
                with tqdm(total=100, desc="Compiling and Uploading", ncols=100) as pbar:
                    for i in range(10):
                        pbar.update(10)
                        time.sleep(0.5)  # Simulate progress

                    env = os.environ.copy()
                    env['PLATFORMIO_UPLOAD_PORT'] = port
                    result = subprocess.run(
                        ['platformio', 'run', '-t', 'upload'],
                        cwd=pio_project_dir,
                        check=True,
                        env=env,
                        capture_output=True
                    )
                    pbar.update(10)
                response = {
                    'status': 'success',
                    'output': result.stdout.decode(),
                    'message': f'Success message for table {table_id}'
                }
            except subprocess.CalledProcessError as e:
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
        request_type = data.get('request_type')
        table_id = data.get('table_id')

        # Save the request to the database
        new_request = FanaCallRequest(
            request_type=request_type,
            table_id=table_id,
            timestamp=timezone.now()
        )
        new_request.save()

        return JsonResponse({'status': 'success', 'message': 'Request logged successfully'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
