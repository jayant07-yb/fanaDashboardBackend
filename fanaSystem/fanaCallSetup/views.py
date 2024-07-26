from django.shortcuts import render
from django.http import JsonResponse
from .forms import SetupForm
import subprocess
import os
from tqdm import tqdm
import time
import serial.tools.list_ports

def generate_esp32_code(wifi_name, wifi_password, table_id):
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'fanaCallSetup', 'esp32_code_template.cpp')
    with open(template_path, 'r') as template_file:
        code = template_file.read()
    code = code.replace('{wifi_name}', wifi_name).replace('{wifi_password}', wifi_password).replace('{table_id}', table_id)
    return code

def get_com_ports():
    ports = serial.tools.list_ports.comports()
    return [(port.device, port.description) for port in ports]

# In your setup_view function, pass the available COM ports to the template
def fana_call_setup_view(request):
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
    return render(request, 'setup.html', {'form': form})
