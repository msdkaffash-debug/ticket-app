from kavenegar import *

API_KEY = "YOUR_API_KEY"

def send_sms(phone, message):
    api = KavenegarAPI(API_KEY)

    params = {
        'receptor': phone,
        'message': message
    }

    return api.sms_send(params)
