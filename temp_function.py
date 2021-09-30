def trading():
    while True:
        daily_profit = [x['profit'] for x in account.trades if x['date'] == datetime.now().strftime("%d/%m/%Y")]
        for crypto in tickers:
            if crypto.current > 0 and len(crypto.price_history) > 0 and len(account.assets) > 0:
                crypto.rsi_val = rsi(crypto.price_history + [crypto.current])
                crypto.macd_val = calcMacd(crypto.price_history + [crypto.current])
                try:
                    if crypto.bought_value is None and crypto.bought_quantity is None and account.TOTAL >= 30 and sum(
                            daily_profit) > -1 and datetime.now().strftime("%A") not in ['Saturday', 'Sunday'] and datetime.today()>=crypto.ban:
                        if 13 < crypto.rsi_val < 28 and crypto.macd_val < 0:
                            crypto.buy(random.randint(11, 18))
                    elif crypto.bought_value is not None and crypto.profit != 0:
                        if datetime.now().strftime("%A") in ['Saturday', 'Sunday']:
                            if crypto.profit_per > crypto.profit_aim:
                                crypto.sell()
                                crypto.profit_aim = random.randint(3, 7) / 10
                        elif crypto.profit_per < -1.5 and crypto.rsi_val>50 or crypto.profit_per > crypto.profit_aim or crypto.rsi_val>65:
                            if crypto.profit_per<-2.0:
                                crypto.ban = datetime.date.today() + datetime.timedelta(days=1)
                            crypto.sell()
                            crypto.profit_aim = random.randint(3, 7) / 10
                        elif crypto.profit_per < -0.5 and crypto.rsi_val < 13 and crypto.profit_aim < 1:
                            if account.TOTAL + crypto.bought_busd >= 30:
                                crypto.sell()
                                crypto.buy(30)
                                crypto.profit_aim = 1.1
                except Exception as e:
                    print_exception()
        time.sleep(0.05)