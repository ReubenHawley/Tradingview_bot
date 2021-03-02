#!/usr/bin/python3
from traceback import print_exc
from flask import request, render_template
from py.TV_bot import app
from ast import literal_eval
import threading
from py.TV_bot.core.account import Account

"""TRADE PARAMETERS"""
SYMBOL_LIST = [{"symbol": "BTC/USDT", "max_trades": 120, 'premium': 1.02, 'minimum_trade_size': 10}]


@app.route('/')
@app.route('/dashboard/')
# visible dashboard which to view and interact
def dashboard():
    return render_template('dashboard.html', symbols=SYMBOL_LIST)


@app.route('/account')
# visible dashboard which to view and interact
def account():
    account2 = traders['result'][1]
    user2 = Account(name=account2['username'],
                    api_k=account2['api_key'],
                    api_s=account2['api_secret'])

    account3 = traders['result'][2]
    user3 = Account(name=account3['username'],
                    api_k=account3['api_key'],
                    api_s=account3['api_secret'])
    return render_template('account.html',
                           usdt_balance=user1.available_balance(),
                           btc_holdings=user1.btc_holdings(),
                           total_usdt_value=user1.account_value(),
                           coins1=user1.account_holdings(),
                           coins2=user2.account_holdings(),
                           coins3=user3.account_holdings(),
                           )


@app.route('/trade_history')
# visible dashboard which to view and interact
def trade_history():
    trades = []
    for symbol in SYMBOL_LIST:
        trades += user1.exchange.fetch_my_trades(symbol["symbol"])
        trades.reverse()

    return render_template('trade_history.html', trades=trades, symbols=SYMBOL_LIST)


@app.route('/orders')
def orders():
    open_orders = []
    for symbol in SYMBOL_LIST:
        open_orders += user1.exchange.fetch_open_orders(symbol['symbol'])
    open_orders.reverse()
    btc = user1.exchange.fetch_ticker('BTC/USDT')['close']
    return render_template('orders.html',
                           open_orders=open_orders,
                           btc=btc)


@app.route('/webhook', methods=['POST'])
# webhook for receiving of orders
def webhook():
    try:
        " capture the webhook through a listener into a variable called webhook_message"
        webhook_message = request.data
        # " parse the text into json format"
        webhook_message = literal_eval(webhook_message.decode('utf8'))  # decoding from bytes to json
        trade_parameters = list(webhook_message.values())

        "iterate over database for all users that subscribe to the strategy . twopercent:'true' "
        cursor.execute(""" SELECT * FROM users WHERE twopercent='true' """)
        traders = dict(result=[dict(r) for r in cursor.fetchall()])
        threads = []
        for symbol in SYMBOL_LIST:
            for trader in traders['result']:
                user = Account(name=trader['username'],
                               api_k=trader['api_key'],
                               api_s=trader['api_secret'])
                t1 = threading.Thread(target=user.market_maker, args=(symbol['symbol'],symbol['max_trades'],
                                                                      symbol['premium'],symbol['minimum_trade_size'],
                                                                      trade_parameters,))
                t1.start()
                threads.append(t1)
        connection.commit()
        for thread in threads:
            thread.join()
        return f"Trade successfully executed"

    except Exception as error:
        print('type is:', error.__class__.__name__)
        print('error occurred,closing database')
        cursor.close()
        print_exc()

