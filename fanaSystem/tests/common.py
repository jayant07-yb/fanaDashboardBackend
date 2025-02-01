# PUBLIC_IP OR DOMAIN RELATED SETTINGS
PUBLIC_IP = "internals.getfana.com"

# Construct the full URL for the authentication endpoint
BASE_URL = f"https://{PUBLIC_IP if PUBLIC_IP else 'localhost:8000'}"
AUTH_SERVER_LOGIN_URL = f"{BASE_URL}/fanaAuthenticator/api/token/"
WSL_SERVER_URL = f"wss://{PUBLIC_IP if PUBLIC_IP else 'localhost:8000'}/ws/dashboard/"
SEND_ORDER_TO_DASHBOARD_URL =  f"{BASE_URL}/fanaDashboard/receiveOrder/"

# For wss --> use https socket i.e. 80 internals.getfana.com
# For ws --> use http socket i.e. internals.getfana.com:8001