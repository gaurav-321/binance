import os
import random
import threading
import time

from binance.client import Client

import config
from algo.functions import rsi, calcMacd

tickers_name = ['YFIBUSD', 'BTCBUSD', 'MKRBUSD', 'ETHBUSD', 'BOTBUSD', 'YFIIBUSD', 'AUTOBUSD', 'PAXGBUSD', 'BULLBUSD',
                'BIFIBUSD', 'BCHBUSD', 'COMPBUSD', 'AAVEBUSD', 'KSMBUSD', 'XRPBEARBUSD', 'BNBBUSD', 'COVERBUSD',
                'XMRBUSD', 'DASHBUSD', 'LTCBUSD', 'KP3RBUSD', 'ZECBUSD', 'BCHABCBUSD', 'ICPBUSD', 'CREAMBUSD',
                'EGLDBUSD', 'XVSBUSD', 'FILBUSD', 'ETCBUSD', 'NEOBUSD', 'BTGBUSD', 'TRBBUSD', 'ETHBULLBUSD',
                'BTCSTBUSD', 'NMRBUSD', 'BNBBULLBUSD', 'BNBBEARBUSD', 'SOLBUSD', 'BALBUSD', 'PSGBUSD', 'AUCTIONBUSD',
                'LINKBUSD', 'DOTBUSD', 'AVAXBUSD', 'WINGBUSD', 'UNIBUSD', 'BARBUSD', 'FORTHBUSD', 'EOSBEARBUSD',
                'BCHABUSD', 'WAVESBUSD', 'CAKEBUSD', 'JUVBUSD', 'BADGERBUSD', 'SNXBUSD', 'ARBUSD', 'ATOMBUSD',
                'WNXMBUSD', 'PROMBUSD', 'SUSHIBUSD', 'RUNEBUSD', 'UNFIBUSD', 'QTUMBUSD', 'INJBUSD', 'DCRBUSD',
                'ACMBUSD', 'DEXEBUSD', 'LUNABUSD', 'REPBUSD', 'BANDBUSD', 'ETHBEARBUSD', 'DEGOBUSD', 'ALICEBUSD',
                'BURGERBUSD', 'BEARBUSD', 'PERPBUSD', 'NANOBUSD', 'SRMBUSD', 'EOSBUSD', 'OMGBUSD', 'XRPBULLBUSD',
                'MIRBUSD', 'ANTBUSD', 'LITBUSD', 'BNTBUSD', 'AXSBUSD', 'BAKEBUSD', 'XTZBUSD', 'NEARBUSD', '1INCHBUSD',
                'AVABUSD', 'FXSBUSD', 'EOSBULLBUSD', 'SXPBUSD', 'DIABUSD', 'CRVBUSD', 'TKOBUSD', 'KNCBUSD', 'BELBUSD',
                'STRAXBUSD', 'DODOBUSD', 'MATICBUSD', 'FRONTBUSD', 'CVPBUSD', 'FISBUSD', 'ADABUSD', 'AUDIOBUSD',
                'WRXBUSD', 'CTKBUSD', 'ICXBUSD', 'ENJBUSD', 'SFPBUSD', 'ALPHABUSD', 'TOMOBUSD', 'IOTABUSD', 'ONTBUSD',
                'ZRXBUSD', 'SWRVBUSD', 'XRPBUSD', 'EPSBUSD', 'SUPERBUSD', 'GBPBUSD', 'UFTBUSD', 'GHSTBUSD', 'ALGOBUSD',
                'PHABUSD', 'EURBUSD', 'GRTBUSD', 'HARDBUSD', 'MANABUSD', 'CTSIBUSD', 'BATBUSD', 'OCEANBUSD', 'DAIBUSD',
                'PAXBUSD', 'VIDTBUSD', 'AUDBUSD', 'TWTBUSD', 'FLMBUSD', 'BZRXBUSD', 'XLMBUSD',
                'CFXBUSD', 'LRCBUSD', 'SKLBUSD', 'LENDBUSD', 'STRATBUSD', 'DOGEBUSD', 'KMDBUSD']


def get_balance(in_ticker):
    return float(client.get_asset_balance(in_ticker)['free'])


def get_all_coin():
    return [(x['asset'], float(x['free'])) for x in client.get_account()['balances'] if float(x['free']) > 0]


def screen_clear():
    if os.name == 'posix':
        _ = os.system('clear')
    else:
        _ = os.system('cls')


def update_ticker():
    temp = {}
    for x in client.get_all_tickers():
        if x['symbol'] in tickers_name:
            temp[x['symbol']] = float(x['price'])
    for name, current in zip(temp.keys(), temp.values()):
        tickers[name].current = current


class Ticker:
    def __init__(self, name):
        self.price_history = []
        self.name = name
        self.bought = {"total_bought": 1, "bought_value": 1}

    def buy(self):
        try:
            quantity = float(format(1 / tickers[self.name].current * 12, '.3f'))
            order_buy = client.create_test_order(
                symbol=self.name,
                side=Client.SIDE_BUY,
                type=Client.ORDER_TYPE_MARKET,
                quantity=quantity)
            return order, f"bought {self.name} for {float(order_buy['fills'][0]['price']) * float(order_buy['fills'][0]['qty'])}"
        except Exception as e:
            print(f"{quantity} of {self.name} failed " + str(e))
            return

    def sell(self):
        quantity = self.bought['total_bought']
        order_sell = client.create_test_order(
            symbol=self.name,
            side=Client.SIDE_SELL,
            type=Client.ORDER_TYPE_MARKET,
            quantity=quantity)
        self.bought = {"total_bought": 1, "bought_value": 1}
        return order, f"sold {self.name} for {float(order_sell['fills'][0]['price']) * float(order_sell['fills'][0]['qty'])}"

    def update_hist(self):
        while True:
            time.sleep(random.randint(1, 30))
            hist = client.get_historical_klines(symbol=self.name, interval="5m", limit=100,
                                                start_str=str(time.time() - 1000000))
            tickers[self.name].price_history = [float(x[4]) for x in hist]
            time.sleep(300)


class Account:
    def __init__(self):
        self.assets = {}
        self.balance = 0
        self.trades = []
        self.file = open("trades.txt", "w")

    def update(self):
        self.balance = 0
        for x, y in get_all_coin():
            self.assets[x] = y
            if x != "BUSD":
                self.balance += tickers[x + "BUSD"].current * y
            else:
                self.balance += y

    def add_trade(self, trade, rate):
        self.trades.append(trade)
        self.file.write(rate + str(trade) + "\n")
        self.file.flush()


client = Client(config.key, config.security)
print("logged in")

account = Account()
tickers = {}
for x in tickers_name:
    tickers[x] = Ticker(x)
    threading.Thread(target=tickers[x].update_hist).start()

while True:
    update_ticker()
    account.update()
    screen_clear()
    print(account.assets, account.balance)

    for tick in tickers_name:
        try:
            ticker = tickers[tick]
            rsi_val = rsi(ticker.price_history + [ticker.current])
            macd_val = calcMacd(ticker.price_history + [ticker.current])
            if rsi_val < 30 and macd_val < 0:
                if len(ticker.price_history) > 0:
                    order, bought = ticker.buy()
                    print(f"Bought  {rsi_val} is rsi and macd {macd_val} of {tick} current {tickers[tick].current}")
                    account.add_trade(order, bought)

            if ticker.name.replace('BUSD', '') in account.assets:
                current_bought = account.assets[tick.replace('BUSD', '')] * ticker.current
                if current_bought > 1:
                    profit = ticker.current - ticker.bought_value if ticker.bought_value != 0 else 1
                    print(f"checking {tick} current price {current_bought}")
                    if rsi_val > 70 and macd_val > 0 or profit / ticker.bought_value * 100 > 0.4:
                        if tick in account.assets and account.assets[tick] > 0:
                            try:
                                order, sold = ticker.sell()
                                account.add_trade(order, sold)
                            except Exception as e:
                                print("Unable to sell due to low amount" + str(e))
        except Exception as e:
            print(e)
            pass
        else:
            pass
