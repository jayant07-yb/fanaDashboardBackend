from decouple import config
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import random
from fanaSystem.utils import generic_error_handler




def generate_otp(length = 6):
    try:
        return ''.join([str(random.randint(0, 9)) for _ in range(length)])
    except Exception as e:
        generic_error_handler(e)

def send_otp(phone_number , otp ,length = 6):
    try:
        client = Client(config('SID') , config('AUTH_TOKEN'))
        message = client.messages.create(
            body=f'Your OTP is: {otp}',
            from_=config('PH'),
            to=phone_number
        )
        return {"success" : True , "message" : "Otp Sent Successfully !"}
    except TwilioRestException as e:
        return generic_error_handler(e , "Twilio Error")
    except Exception as e:
        return generic_error_handler(e)