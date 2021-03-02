from py.TV_bot.core.account import Account
import sqlite3
from py.TV_bot.core import find_user_info as getUsers
import time
import csv

if __name__ == '__main__':
    try:
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
            if trade['side'] =='sell':
                total_of_trades += trade['cost']
        daily_return = (total_of_trades/100)*2
        "execute buy order based on trade profits"
        print(daily_return)
        while True:
            free = user.exchange.fetch_free_balance()
            if daily_return < free['USDT']:
                close = user.exchange.fetch_ticker('BTC/USDT')['close']
                buy = 11/close # change the value  "value/close" amount when testing
                response = user.exchange.create_market_buy_order('BTC/USDT', buy)
                trade_data = [response['timestamp'],
                              response['symbol'],
                              response['side'],
                              response['price'],
                              response['amount'],
                              response['cost'],
                              response['fee']['cost']
                              ]
                if response:
                    with open('../trade_data/executed_trades.csv', mode='a') as output_file:
                        csv_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        csv_writer.writerow(trade_data)
                    exit()
            else:
                time.sleep(60)
                continue
    except ConnectionError:
        print('shit went very wrong.... please try again')
