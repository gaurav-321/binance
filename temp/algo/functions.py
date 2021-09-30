import os
from sys import exc_info
from traceback import format_exception
import pandas as pd
import sentry_sdk
import flask_login

def print_exception():
    etype, value, tb = exc_info()
    info, error = format_exception(etype, value, tb)[-2:]
    print(f'Exception in:\n{info}\n{error}')


def rsi(a):
    rsi_val = 0
    try:
        data = pd.DataFrame(a, columns={"temp"})
        close = data[f'{"temp"}']
        # Get the difference in price from previous step
        delta = close.diff()

        # Get rid of the first row, which is NaN since it did not have a previous
        # row to calculate the differences
        delta = delta[1:]

        # Make the positive gains (up) and negative gains (down) Series
        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0

        # Calculate the EWMA
        roll_up1 = up.ewm(span=12).mean()
        roll_down1 = down.abs().ewm(span=12).mean()

        # Calculate the RSI based on EWMA
        RS1 = roll_up1 / roll_down1
        RSI1 = 100.0 - (100.0 / (1.0 + RS1))
        list_rsi = [0]
        for element in RSI1:
            list_rsi.append(element)
        rsi_val = list_rsi[-1]

    except Exception as e:
        pass

    return rsi_val


def calcMacd(priceArray):
    def calcMultiplier(number):
        return 2 / float(number + 1)

    def calcEMA(close, multiplier, avgDays):
        return close * multiplier + avgDays * (1 - multiplier)

    lowEMA = 12
    highEMA = 26
    signalChar = 9

    blueLine = 0
    redLine = 0
    signal = 0
    signalCount = 0

    for i in range(0, len(priceArray)):
        tempPrice = int(float(priceArray[i]))
        if i < lowEMA:
            blueLine += tempPrice
        elif i == lowEMA:
            blueLine /= lowEMA
            blueLine = calcEMA(tempPrice, calcMultiplier(lowEMA), blueLine)
        else:
            blueLine = calcEMA(tempPrice, calcMultiplier(lowEMA), blueLine)
        if i < highEMA:
            redLine += tempPrice
        elif i == highEMA:
            redLine /= highEMA
            redLine = calcEMA(tempPrice, calcMultiplier(highEMA), redLine)
        else:
            redLine = calcEMA(tempPrice, calcMultiplier(highEMA), redLine)
            if signalCount < signalChar:
                signal += blueLine - redLine
            elif signalCount == signalChar:
                signal /= signalChar
                signal = calcEMA((blueLine - redLine), calcMultiplier(signalChar), signal)
            else:
                signal = calcEMA((blueLine - redLine), calcMultiplier(signalChar), signal)
            signalCount += 1
    macD = blueLine - redLine
    return macD


tickers_name = [('YFIBUSD', 6), ('BNBBUSD', 4), ('BTCBUSD', 6), ('MKRBUSD', 5), ('XVSBUSD', 3), ('ETHBUSD', 5),
                ('YFIIBUSD', 6), ('AUTOBUSD', 6), ('BIFIBUSD', 5), ('BCHBUSD', 5), ('AAVEBUSD', 4), ('COMPBUSD', 5),
                ('COVERBUSD', 5), ('XMRBUSD', 5), ('DASHBUSD', 5), ('LTCBUSD', 5), ('KP3RBUSD', 5), ('ZECBUSD', 5),
                ('ICPBUSD', 2), ('CREAMBUSD', 4), ('EGLDBUSD', 4), ('FILBUSD', 4), ('ETCBUSD', 3), ('BTCSTBUSD', 3),
                ('BTGBUSD', 3), ('NEOBUSD', 3), ('TRBBUSD', 3), ('NMRBUSD', 3), ('SOLBUSD', 3), ('BALBUSD', 3),
                ('PSGBUSD', 3), ('AUCTIONBUSD', 3), ('LINKBUSD', 3), ('DOTBUSD', 3), ('AVAXBUSD', 3), ('UNIBUSD', 3),
                ('BARBUSD', 3), ('WINGBUSD', 3), ('FORTHBUSD', 3), ('BCHABUSD', 3), ('WAVESBUSD', 3), ('CAKEBUSD', 3),
                ('JUVBUSD', 3), ('BADGERBUSD', 3), ('SNXBUSD', 3), ('SUSHIBUSD', 3), ('ATOMBUSD', 3),
                ('RUNEBUSD', 3), ('PROMBUSD', 3), ('INJBUSD', 3), ('ACMBUSD', 3), ('QTUMBUSD', 3), ('UNFIBUSD', 3),
                ('LUNABUSD', 3), ('DEXEBUSD', 3), ('BANDBUSD', 3), ('PERPBUSD', 3), ('DEGOBUSD', 3), ('BURGERBUSD', 1),
                ('ALICEBUSD', 2), ('NANOBUSD', 2), ('MIRBUSD', 3), ('SRMBUSD', 2), ('EOSBUSD', 2), ('OMGBUSD', 2),
                ('BNTBUSD', 2), ('ANTBUSD', 2), ('BAKEBUSD', 2), ('AXSBUSD', 2), ('NEARBUSD', 2), ('LITBUSD', 2),
                ('XTZBUSD', 2), ('1INCHBUSD', 2), ('AVABUSD', 2), ('FXSBUSD', 3), ('DIABUSD', 3), ('SXPBUSD', 2),
                ('POLSBUSD', 2), ('MATICBUSD', 1), ('CRVBUSD', 3), ('TKOBUSD', 2), ('KNCBUSD', 3), ('STRAXBUSD', 2),
                ('BELBUSD', 2), ('DODOBUSD', 3), ('FISBUSD', 3), ('ADABUSD', 2), ('GBPBUSD', 2), ('CVPBUSD', 2),
                ('FRONTBUSD', 2), ('CTKBUSD', 2), ('AUDIOBUSD', 2), ('WRXBUSD', 2), ('TOMOBUSD', 2), ('ENJBUSD', 2),
                ('ALPHABUSD', 2), ('ICXBUSD', 2), ('GHSTBUSD', 2), ('EURBUSD', 2), ('IOTABUSD', 2), ('ONTBUSD', 2),
                ('SFPBUSD', 2), ('XRPBUSD', 2), ('ZRXBUSD', 2), ('SWRVBUSD', 3), ('EPSBUSD', 3), ('USDCBUSD', 2),
                ('TUSDBUSD', 2), ('PAXBUSD', 2), ('ALGOBUSD', 2), ('UFTBUSD', 2), ('SUPERBUSD', 3), ('PHABUSD', 2),
                ('HARDBUSD', 2), ('MANABUSD', 2), ('GRTBUSD', 2), ('AUDBUSD', 1), ('BATBUSD', 2), ('CTSIBUSD', 1),
                ('OCEANBUSD', 2), ('VIDTBUSD', 2), ('TWTBUSD', 2), ('FLMBUSD', 2), ('XLMBUSD', 1), ('CFXBUSD', 3),
                ('BZRXBUSD', 2), ('LRCBUSD', 1), ('DOGEBUSD', 1)][:50]


def get_asset(client):
    return [(x['asset'], float(x['free'])) for x in client.get_account()['balances'] if float(x['free']) > 0]


def screen_clear():
    if os.name == 'posix':
        _ = os.system('clear')
    else:
        _ = os.system('cls')


def set_sentry():
    sentry_sdk.init(
        "https://b976b4679bf2498ab079f05eeb3bc441@o565437.ingest.sentry.io/5773117",

        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0
    )

def trading_old():
    while True:
        for crypto in tickers:
            if crypto.current > 0 and len(crypto.price_history) > 0 and len(account.assets) > 0:
                rsi_val = rsi(crypto.price_history + [crypto.current])
                macd_val = calcMacd(crypto.price_history + [crypto.current])
                try:
                    if crypto.bought_value is None and crypto.bought_quantity is None and account.TOTAL >= 14:
                        if rsi_val < 30 and macd_val < 0:
                            if rsi_val<26:
                                crypto.buy(18 if account.TOTAL>=18 else 14)
                    elif account.check_holding(crypto.name) or crypto.bought_value is not None:
                        if rsi_val > 65 and macd_val > 0 and crypto.profit_per > 0 or crypto.profit_per > 0.5 or crypto.profit_per < -1.2 and rsi_val<27:
                            crypto.sell()
                except Exception as e:
                    print_exception()
        time.sleep(0.05)