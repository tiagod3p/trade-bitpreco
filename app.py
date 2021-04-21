import requests

DOMAIN = 'https://api-simulator.bitpreco.com' ## dev environment bitpreco
API_KEY = ""
SIGNATURE = ""
AUTH_TOKEN = API_KEY + SIGNATURE

def info_coin(cryptoName):
    response = dict(requests.get(
        f'{DOMAIN}/{cryptoName.lower()}-brl/ticker').json())
    return response