import requests

DOMAIN = 'https://api-simulator.bitpreco.com' ## dev environment bitpreco
API_KEY = ""
SIGNATURE = ""
AUTH_TOKEN = API_KEY + SIGNATURE

def info_crypto(cryptoName):
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


def buy(crypto, buy_price, buy_amount_crypto):
    data_buy = json.dumps({"cmd": "buy", "market": f"{crypto.upper()}-BRL", "price": buy_price,
                           "amount": buy_amount_crypto, "auth_token": AUTH_TOKEN})
    return api_call(data_buy)['order_id']


def sell(crypto, sell_price, sell_amount_crypto):
    data_sell = json.dumps({"cmd": "sell", "market": f"{crypto.upper()}-BRL", "price": sell_price,
                            "amount": sell_amount_crypto, "auth_token": AUTH_TOKEN})
    return api_call(data_sell)