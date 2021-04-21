from time import sleep, localtime, asctime
from datetime import datetime
from operator import itemgetter as destructuring
import json
import threading
import traceback

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

def operation(crypto, buy_price, buy_amount):
    order_id = buy(crypto, buy_price, buy_amount)
    amount, price, cost, market, time_stamp = check_status(
        order_id)

    if not amount:
        return

    PROFIT_PERCENTAGE = 5 ## percentage of profit that you want sell
    profit = price * (1 + ( PROFIT_PERCENTAGE * 0.01 ))
    response_sell = sell(crypto, profit, amount)

    print('Operation: ',
          response_sell['message_cod'], asctime(localtime()))


while(True):
    try:
        sleep(30)

        response_eth = info_crypto('eth')
        response_btc = info_crypto('btc')

        buy_btc = destructuring('buy')(response_btc)
        buy_eth = destructuring('buy')(response_eth)

        data_balance = json.dumps({"cmd": "balance", "auth_token": AUTH_TOKEN})
        response_balance = api_call(data_balance)

        brl = response_balance['BRL'] ## BRL Quantity available to trade

        buy_amount_btc, buy_amount_eth = (brl/2)/buy_btc, (brl/2)/buy_eth ## quantity available to trade ethereum and bitcoin

        if buy_amount_btc >= 0.001 and buy_amount_eth >= 0.01: ## minimum amount to buy on bitpreco
            threading.Thread(target=operation, args=('btc', buy_btc, buy_amount_btc)).start()
            threading.Thread(target=operation, args=('eth', buy_eth, buy_amount_eth)).start()

        elif brl/buy_eth >= 0.01: ## only buy eth
            operation('ETH', buy_eth, brl/buy_eth)
    except Exception as err:
        tb = traceback.format_exc()
        print(err, asctime(localtime()))
        print(tb)
