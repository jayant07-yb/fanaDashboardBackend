import os
import json
import subprocess
import serial.tools.list_ports

def get_com_ports():
    ports = serial.tools.list_ports.comports()
    return [(port.device, f"{port.device} - {port.description}") for port in ports]

def generate_esp32_code(wifi_name, wifi_password, table_id, server_ip):
    server_url = f"http://{server_ip}:8000/fanaDashboard/handleFanaCall/"
    template_path = os.path.join(os.path.dirname(__file__), 'tmp_non_reset_pin_code.cpp')

    with open(template_path, 'r') as template_file:
        code = template_file.read()

    code = code.replace('{wifi_name}', wifi_name)
    code = code.replace('{wifi_password}', wifi_password)
    code = code.replace('{server_url}', server_url)
    code = code.replace('{table_id}', table_id)

    return code

def update_platformio_ini(board_type):
    ini_path = os.path.join(os.path.dirname(__file__), '..', 'platformio.ini')
    
    with open(ini_path, 'r') as file:
        lines = file.readlines()

    # Modify or add board type
    for i, line in enumerate(lines):
        if line.startswith("board ="):
            lines[i] = f"board = {board_type}\n"
            break
    else:
        lines.append(f"\nboard = {board_type}\n")

    with open(ini_path, 'w') as file:
        file.writelines(lines)

def main():
    print("Fana Call ESP32 Setup CLI")

    # Take user inputs
    server_ip = input("Enter Server IP: ")
    table_id = input("Enter Table ID: ")
    wifi_name = input("Enter WiFi Name: ")
    wifi_password = input("Enter WiFi Password: ")

    # List available COM ports
    com_ports = get_com_ports()
    if not com_ports:
        print("No COM ports detected. Please connect your ESP32.")
        return

    print("Available COM ports:")
    for i, (port, desc) in enumerate(com_ports):
        print(f"{i + 1}. {desc}")

    port_choice = int(input("Select a port (number): ")) - 1
    port = com_ports[port_choice][0]

    board_type = input("Enter ESP32 Board Type (default: esp32dev): ") or "esp32dev"
    
    # Generate ESP32 code
    code = generate_esp32_code(wifi_name, wifi_password, table_id, server_ip)

    # Save the generated code
    src_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
    if not os.path.exists(src_dir):
        os.makedirs(src_dir)

    with open(os.path.join(src_dir, 'main.cpp'), 'w') as f:
        f.write(code)

    # Update platformio.ini with the correct board type
    update_platformio_ini(board_type)

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

        print("[SUCCESS] Code uploaded successfully!")
        print(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print("[ERROR] Upload failed!")
        print(e.stderr.decode())

if __name__ == "__main__":
    main()
