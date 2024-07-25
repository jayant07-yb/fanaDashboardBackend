from flask import Flask, request, jsonify
import subprocess
import os
import logging
from tqdm import tqdm
import time

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

def generate_esp32_code(wifi_name, wifi_password):
    with open('esp32_code_template.cpp', 'r') as template_file:
        code = template_file.read()
    code = code.replace('{wifi_name}', wifi_name).replace('{wifi_password}', wifi_password)
    return code

@app.route('/setup', methods=['POST'])
def setup():
    try:
        data = request.json
        app.logger.debug(f"Received data: {data}")

        if not data:
            raise ValueError("No data provided")
        
        table_id = data.get('table_id')
        wifi_name = data.get('wifi_name')
        wifi_password = data.get('wifi_password')
        port = data.get('port')

        if not all([table_id, wifi_name, wifi_password, port]):
            raise ValueError("Missing required parameters")

        # Generate Arduino code
        code = generate_esp32_code(wifi_name, wifi_password)

        if not os.path.exists('src'):
            os.makedirs('src')
        with open('src/main.cpp', 'w') as f:
            f.write(code)

        # Show progress bar during compilation and upload
        with tqdm(total=100, desc="Compiling and Uploading", ncols=100) as pbar:
            for i in range(10):
                pbar.update(10)
                time.sleep(0.5)  # Simulate progress

            env = os.environ.copy()
            env['PLATFORMIO_UPLOAD_PORT'] = port
            compile_upload = subprocess.run(
                ['platformio', 'run', '-t', 'upload'],
                check=True, env=env, capture_output=True
            )
            pbar.update(10)
        
        app.logger.info(f"PlatformIO Output: {compile_upload.stdout.decode()}")
        return jsonify({'status': 'success', 'output': compile_upload.stdout.decode()}), 200

    except subprocess.CalledProcessError as e:
        app.logger.error(f"PlatformIO Error: {e.stderr.decode()}")
        return jsonify({'status': 'error', 'message': e.stderr.decode()}), 500
    except ValueError as ve:
        app.logger.error(f"ValueError: {ve}")
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        app.logger.error(f"Unexpected Error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/data', methods=['POST'])
def data():
    try:
        data = request.json
        app.logger.debug(f"Received data: {data}")

        if not data:
            raise ValueError("No data provided")
        
        app.logger.info(f"Received data: {data}")
        return jsonify({'status': 'success'}), 200
    except ValueError as ve:
        app.logger.error(f"ValueError: {ve}")
        return jsonify({'status': 'error', 'message': str(ve)}), 400
    except Exception as e:
        app.logger.error(f"Unexpected Error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
