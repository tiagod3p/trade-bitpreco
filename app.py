import requests

DOMAIN = 'https://api-simulator.bitpreco.com' ## dev environment bitpreco
API_KEY = ""
SIGNATURE = ""
AUTH_TOKEN = API_KEY + SIGNATURE

def info_coin(cryptoName):
    response = dict(requests.get(
        f'{DOMAIN}/{cryptoName.lower()}-brl/ticker').json())
    return response


def trade(data):
    headers = {'Content-Type': 'application/json'}
    response = requests.post(
        f'{DOMAIN}/trading/', headers=headers, data=data).json()
    if response['success'] is True:
        return response
    else:
        raise Exception('api-call err', response['message_cod'], asctime(localtime()))

