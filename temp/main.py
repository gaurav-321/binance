import random
import threading
import time
from datetime import datetime, timedelta

from binance import ThreadedWebsocketManager
from binance.client import Client
from colorama import init, Fore

import temp.config as config
from temp.algo.functions import get_asset, print_exception, tickers_name
from temp.algo.functions import rsi, calcMacd

init()
red, green, blue = Fore.RED, Fore.GREEN, Fore.BLUE


class Ticker:
    def __init__(self, name):
        self.price_history = []
        self.name = name
        self.link = f"https://www.binance.com/en/trade/{name.replace('BUSD', '_BUSD')}?type=spot"
        self.bought_value = None
        self.bought_busd = None
        self.bought_quantity = None
        self.current = 0
        self.profit = 0
        self.profit_per = 0
        self.buy_limit = 14
        self.minQty = 0
        self.rsi_val = 0
        self.macd_val = 0
        self.precision = 0
        self.profit_aim = random.randint(3, 7) / 10
        self.ban = datetime.today()

    def buy(self, buy_limit=None):
        if buy_limit:
            quantity = round(1 / self.current * buy_limit, self.precision)
        else:
            quantity = round(1 / self.current * self.buy_limit, self.precision)
        try:
            order_buy = client.create_test_order(
                symbol=self.name,
                side=Client.SIDE_BUY,
                type=Client.ORDER_TYPE_MARKET,
                quantity=quantity)
            self.bought_value = self.current
            self.bought_quantity = quantity
            self.bought_busd = quantity * self.current
            account.TOTAL -= self.bought_busd
            account.add_trade(
                {'name': self.name, 'current': self.current, 'bought': self.bought_value,
                 'bought_busd': self.bought_busd,
                 'quantity': self.bought_quantity, 'rsi': self.rsi_val, 'macd': self.macd_val, 'profit': self.profit,
                 'profit_per': self.profit_per,
                 'link': self.link, 'action': "BUY", "time": datetime.now().strftime("%H %M %S"),
                 "date": datetime.now().strftime("%d/%m/%Y")})
        except Exception as e:
            print(red, self.name, quantity, float(format(1 / self.current * self.buy_limit, f'.6f')), self.current, e)

    def sell(self):
        # quantity = account.assets[self.name.replace("BUSD", "")]
        quantity = self.bought_quantity
        order_sell = client.create_test_order(
            symbol=self.name,
            side=Client.SIDE_SELL,
            type=Client.ORDER_TYPE_MARKET,
            quantity=quantity)
        account.TOTAL += self.bought_busd + self.profit
        account.add_trade(
            {'name': self.name, 'current': self.current, 'bought': self.bought_value,
             'bought_busd': self.bought_busd,
             'quantity': self.bought_quantity, 'rsi': self.rsi_val, 'macd': self.macd_val, 'profit': self.profit,
             'profit_per': self.profit_per,
             'link': self.link, 'action': "SELL", "time": datetime.now().strftime("%H %M %S"),
             "date": datetime.now().strftime("%d/%m/%Y")})
        self.bought_value = None
        self.bought_quantity = None
        self.bought_busd = None
        self.profit = 0
        self.profit_per = 0

    def update_hist(self):
        time.sleep(random.randint(1, len(tickers_name)))
        while True:
            try:
                hist = client.get_historical_klines(self.name, Client.KLINE_INTERVAL_5MINUTE, "1 day ago UTC")
                self.price_history = [float(x[4]) for x in hist]
                time.sleep(300)
            except Exception as e:
                pass

    def update(self, data):
        self.current = float(data['b'])
        if self.bought_value is not None:
            profit = self.current - self.bought_value
            self.profit_per = float(format(profit / self.bought_value * 100 - 0.2, ".4f"))
            self.profit = float(format(self.profit_per * self.buy_limit / 100, ".4f"))


class Account:
    def __init__(self):
        self.assets = {}
        self.balance = 0
        self.trades = []
        self.file = open("trades.csv", "w")
        self.file.write("name, current, bought, quantity, profit, profitper, link, action\n")
        self.TOTAL = 200

    def update(self):
        time.sleep(random.randint(1, 10))
        while True:
            self.file.flush()
            try:
                self.balance = 0
                for x, y in get_asset(client):
                    self.assets[x] = y
                    if x != "BUSD":
                        self.balance += [ticker for ticker in tickers if ticker.name == x + "BUSD"][0].current * y
                    else:
                        self.balance += y
                time.sleep(2)
            except:
                print_exception()

    def add_trade(self, trade):
        print(blue, trade)
        self.trades.append(trade)
        self.file.write(str(",".join([str(x) for x in trade.values()])) + "\n")

    def check_holding(self, t_name):
        return True if t_name.replace("BUSD", "") in self.assets and \
                       [ticker for ticker in tickers if ticker.name == t_name][0].current * self.assets[
                           t_name.replace("BUSD", "")] > 10 else False


def update_ticker():
    twm = ThreadedWebsocketManager(api_key=config.key, api_secret=config.security)
    twm.start()
    for crypt in tickers:
        twm.start_symbol_ticker_socket(callback=crypt.update, symbol=crypt.name)


def trading():
    while True:
        daily_profit = [x['profit'] for x in account.trades if x['date'] == datetime.now().strftime("%d/%m/%Y")]
        for crypto in tickers:
            if crypto.current > 0 and len(crypto.price_history) > 0 and len(account.assets) > 0:
                crypto.rsi_val = rsi(crypto.price_history + [crypto.current])
                crypto.macd_val = calcMacd(crypto.price_history + [crypto.current])
                try:
                    if crypto.bought_value is None and crypto.bought_quantity is None and account.TOTAL >= 30 and sum(
                            daily_profit) > -2: #and datetime.now().strftime("%A") not in ['Saturday', 'Sunday']:
                        if crypto.rsi_val < 26 and crypto.macd_val < 0:
                            crypto.buy(random.randint(11, 20))
                    elif crypto.bought_value is not None and crypto.profit != 0:
                        if crypto.rsi_val > 60:
                            crypto.sell()
                except Exception as e:
                    print_exception()
        time.sleep(0.05)


client = Client(config.key, config.security)
print(green + "logged in")
tickers = []
account = Account()

client.get_ticker()


def main():
    for x, precision in tickers_name:
        ticker = Ticker(x)
        ticker.precision = precision
        tickers.append(ticker)
        threading.Thread(target=ticker.update_hist).start()
    threading.Thread(target=account.update).start()
    threading.Thread(target=update_ticker).start()
    threading.Thread(target=trading).start()


main()
