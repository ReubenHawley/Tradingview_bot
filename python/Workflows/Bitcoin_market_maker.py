import time
from python.core.account import Account
from python.core.Strategy import Strategy
from termcolor import colored
import threading

""""instantiate account"""
reuben = Account()
HFT = Strategy(reuben)


def place_trade(symbol, sleeptime):
    entry_order_response = HFT.order(symbol['symbol'], 'MARKET', "BUY", symbol['trade_size'], '')
    'check to see if we received a valid trade entry'
    if entry_order_response:
        print(colored(entry_order_response, 'green'))
        'calculate a profit markup on the entry price'
        selling_price = entry_order_response['price'] * symbol['premium']
        'capture the exit order response'
        exit_order_response = HFT.order(symbol['symbol'], 'LIMIT', "SELL", symbol['trade_size'], selling_price)
        print(colored(exit_order_response, 'green'))
        'purposefully sleep for (X) sec to as to not exceed rate limit for binance'
        if exit_order_response:
            print(colored(f"all trades successfully submitted, sleeping for {sleeptime}", 'blue'))
            time.sleep(sleeptime)
        else:
            print(colored('error occurred', "red"))
            time.sleep(sleeptime*60)


def start_strategy(symbol, time_to_sleep):
    while True:
        if len(reuben.exchange.fetch_open_orders(symbol['symbol'])) < symbol['max_trades']:
            if len(reuben.exchange.fetch_open_orders(symbol['symbol'])) <= 10:
                print(f"current trades:{len(reuben.exchange.fetch_open_orders(symbol['symbol']))}/{symbol['max_trades']} open")
                place_trade(symbol, time_to_sleep)
            elif 11 <= len(reuben.exchange.fetch_open_orders(symbol['symbol'])) <= 20:
                print(f"current trades:{len(reuben.exchange.fetch_open_orders(symbol['symbol']))}/{symbol['max_trades']} open")
                place_trade(symbol, time_to_sleep*30)
            elif 21 <= len(reuben.exchange.fetch_open_orders(symbol['symbol'])) <= 30:
                print(f"current trades:{len(reuben.exchange.fetch_open_orders(symbol['symbol']))}/{symbol['max_trades']} open")
                place_trade(symbol, time_to_sleep*60)
            else:
                print(f"current trades:{len(reuben.exchange.fetch_open_orders(symbol['symbol']))}/{symbol['max_trades']} open")
                place_trade(symbol, time_to_sleep*90)


if __name__ == '__main__':
    sleepytime = 5
    SYMBOL_LIST = [{"symbol": "SXP/USDT", "max_trades": 40, 'trade_size': 10, 'premium': 1.005},
                   {"symbol": "SUSHI/USDT", "max_trades": 20, 'trade_size': 2, 'premium': 1.005}
                   ]
    threadlist = []
    for trade_symbol in SYMBOL_LIST:
        t1 = threading.Thread(target=start_strategy, args=(trade_symbol, sleepytime,))
        t1.start()
        threadlist.append(t1)
    for thread in threadlist:
        thread.join()
