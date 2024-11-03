from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import logging

# Configure logging to output to a file
logging.basicConfig(filename='table_activity.log', level=logging.INFO, format='%(asctime)s - %(message)s')


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
