from py.core.account import Account
import sqlite3
from py.core.create_db import find_user_info as getUsers
import time

if __name__ == '__main__':
    "instantiate database"
    connection = sqlite3.connect('../data/tvBot.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    users = getUsers()[0]

    "instantiate exchange connection"
    user = Account(name=users['username'],
                   api_k=users['api_key'],
                   api_s=users['api_secret'])

    "fetch trades to parse for profits"
    since = user.exchange.milliseconds() - 86400000  # -1 day from now
    limit = 1000  # change for your limit
    trades = user.exchange.fetch_my_trades('BTC/USDT', since=since, limit=limit)
    total_of_trades = 0
    for trade in trades:
        if trade['side']:
            total_of_trades += trade['cost']
    daily_return = (total_of_trades/100)*2
    "execute buy order based on trade profits"
    while True:
        free = user.exchange.fetch_free_balance()
        if daily_return < free['USDT']:
            close = user.exchange.fetch_ticker('BTC/USDT')['close']
            buy = daily_return/close
            response = user.exchange.create_market_buy_order('BTC/USDT', buy)
            if response:
                print(response)
                break
        else:
            time.sleep(60)
            continue
