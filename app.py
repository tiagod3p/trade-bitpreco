from time import sleep, localtime, asctime
from operator import itemgetter as destructuring

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


def check_status(order_id):
    while(True):
        sleep(30)
        data_order_status = json.dumps({"cmd": "order_status",
                                        "order_id": order_id, "auth_token": AUTH_TOKEN})

        response_order_status = api_call(data_order_status)
        status, exec_amount, price, cost, market, time_stamp = destructuring(
            'status', 'exec_amount', 'price', 'cost', 'market', 'time_stamp')(response_order_status['order'])

        if status == 'FILLED' and exec_amount > 0:
            return exec_amount, price, cost, market, time_stamp

        diff = datetime.now() - datetime.strptime(time_stamp, "%Y-%m-%d %H:%M:%S")
        THREE_HOURS = (3600*3)

        if diff.seconds > THREE_HOURS:
            data_order_cancel = json.dumps({"cmd": "order_cancel",
                                            "order_id": order_id, "auth_token": AUTH_TOKEN})
            response_order_cancel = api_call(data_order_cancel)

            if status == 'PARTIAL':
                return exec_amount, price, cost, market, time_stamp

            if status == 'EMPTY':
                return '', '', '', '', ''