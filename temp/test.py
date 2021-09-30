import os
import random
import threading
import time
from temp.algo.functions import tickers_name
from binance.client import Client
import math
import config
from algo.functions import rsi, calcMacd
import json

def check_decimals(symbol):
    info = client.get_symbol_info(symbol)
    val = info['filters'][2]['stepSize']
    decimal = 0
    is_dec = False
    for c in val:
        if is_dec is True:
            decimal += 1
        if c == '1':
            break
        if c == '.':
            is_dec = True
    return decimal


client = Client(config.key, config.security)
print("logged in")
temp = {}
for x in client.get_all_tickers():
    if x['symbol'] in tickers_name:
        temp[x['symbol']] = float(x['price'])

new = {}
for x in tickers_name:
    info = client.get_symbol_info(x)
    current = temp[x]
    stepSize = float(info['filters'][2]['stepSize'])
    precision = int(round(-math.log(stepSize, 10), 0))
    quantity = round(1 / current * 11, precision)
    print(x, current, quantity)
    order_buy = client.create_test_order(
        symbol=x,
        side=Client.SIDE_BUY,
        type=Client.ORDER_TYPE_MARKET,
        quantity=quantity)


