import time
from binance.client import Client
from binance.client import Client

import config
from algo.functions import set_sentry, get_asset, screen_clear
from algo.functions import tickers_name
from binance import ThreadedWebsocketManager

def update_ticker():
    twm = ThreadedWebsocketManager(api_key=config.key, api_secret=config.security)
    # start is required to initialise its internal loop
    twm.start()
    for crypt in tickers:
        twm.start_symbol_ticker_socket(callback=crypt.update, symbol=crypt.name)
    """
        while True:
        temp = {}
        for x in client.get_all_tickers():
            if x['symbol'] in tickers_name:
                temp[x['symbol']] = float(x['price'])
        for name, current in zip(temp.keys(), temp.values()):
            crypt = [tick for tick in tickers if tick.name == name][0]
            crypt.current = current
            if crypt.bought_value is not None:
                profit = crypt.current - crypt.bought_value
                crypt.profit_per = profit / crypt.bought_value * 100
                crypt.profit = crypt.profit_per * crypt.buy_limit
            else:
                crypt.profit_per = 0
                crypt.profit = 0
        time.sleep(0.2)"""


class Ticker:
    def __init__(self, name):
        self.price_history = []
        self.name = name
        self.bought_value = None
        self.bought_quantity = None
        self.current = 0
        self.profit = 0
        self.profit_per = 0
        self.buy_limit = 11

    def buy(self):
        try:
            for i in range(2, 9):
                quantity = float(format(1 / self.current * self.buy_limit, f'.{i}f'))
                if quantity != 0:
                    break
            order_buy = client.create_test_order(
                symbol=self.name,
                side=Client.SIDE_BUY,
                type=Client.ORDER_TYPE_MARKET,
                quantity=quantity)
            self.bought_value = self.current
            self.bought_quantity = quantity
            msg = "Current Value:- {}   ,Bought Value:- {}   ,Profit:- {}   ,ProfitPer:- {}%   ,".format(self.current,
                                                                                                         self.bought_value,
                                                                                                         self.profit,
                                                                                                         self.profit_per)
            account.add_trade(msg)
        except Exception as e:
            print(self.name, quantity, float(format(1 / self.current * self.buy_limit, f'.6f')), self.current, e)
            time.sleep(10)

    def sell(self):
        # quantity = account.assets[self.name.replace("BUSD", "")]
        quantity = self.bought_quantity
        order_sell = client.create_test_order(
            symbol=self.name,
            side=Client.SIDE_SELL,
            type=Client.ORDER_TYPE_MARKET,
            quantity=quantity)
        msg = "Current Value:- {}   ,Bought Value:- {}   ,Profit:- {}   ,ProfitPer:- {}%   ,".format(self.current,
                                                                                                     self.bought_value,
                                                                                                     self.profit,
                                                                                                     self.profit_per)
        self.bought_value = None
        self.bought_quantity = None
        account.add_trade(msg)

    def update_hist(self):
        time.sleep(tickers.index(self))
        while True:
            try:
                hist = client.get_historical_klines(symbol=self.name, interval="5m", limit=100,
                                                    start_str=str(time.time() - 1000000))
                self.price_history = [float(x[4]) for x in hist]
                time.sleep(300)
            except Exception as e:
                print(f"failed {self.name} {e}")

    def update(self, data):
        self.current = float(data['c'])
        if self.bought_value is None:
            self.profit=0
            self.profit_per=0
        else:
            profit = self.current - self.bought_value
            self.profit_per = profit / self.bought_value * 100
            self.profit = self.profit_per * self.buy_limit



class Account:
    def __init__(self):
        self.assets = {}
        self.balance = 0
        self.trades = []
        self.file = open("trades.txt", "w")

    def update(self):
        self.balance = 0
        for x, y in get_asset(client):
            self.assets[x] = y
            if x != "BUSD":
                self.balance += [ticker for ticker in tickers if ticker.name == x + "BUSD"][0].current * y
            else:
                self.balance += y

    def add_trade(self, trade):
        print(trade)
        self.trades.append(trade)
        self.file.write(trade + "\n")
        self.file.flush()

    def check_holding(self, t_name):
        return True if t_name.replace("BUSD", "") in self.assets and \
                       [ticker for ticker in tickers if ticker.name == t_name][0].current * self.assets[
                           t_name.replace("BUSD", "")] > 10 else False


if __name__ == "__main__":
    set_sentry()
    client = Client(config.key, config.security)
    print("logged in")

    tickers = []
    for x in tickers_name:
        ticker = Ticker(x)
        tickers.append(ticker)
        # threading.Thread(target=ticker.update_hist).start()
    update_ticker()
    account = Account()

    while True:
        time.sleep(0.8)
        screen_clear()
        for crypt in tickers:
            if crypt.current > 0 and crypt.bought_value is None:
                crypt.buy()
            if crypt.bought_value is not None:
                print(f"{crypt.name} current: {crypt.current} bought: {crypt.bought_value} profit: {crypt.profit} profit_per: {crypt.profit_per}")
                if crypt.profit_per>0.1:
                    crypt.sell()
