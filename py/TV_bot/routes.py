#!/usr/bin/python3
from traceback import print_exc
from flask import request, render_template
from py.TV_bot import app
from ast import literal_eval
import threading
from py.TV_bot.core.futures import Futures
from py.TV_bot.core.account import Account
from py.TV_bot.models import User

"""TRADE PARAMETERS"""
SYMBOL_LIST = [{"symbol": "BTC/BUSD", "max_trades": 160, 'premium': 1.02, 'minimum_trade_size': 10},
               {"symbol": "BTC/USD", "max_trades": 160, 'premium': 1.01, 'minimum_trade_size': 1}]
"Get all accounts for user chris"
UI_accounts = User.query.filter_by(username='chris').all()
"create empty dictionary to which to append"
accounts = {}
"iterate over all sql objects to create dictionary of Account objects"
for key, value in enumerate(UI_accounts):
    accounts[key] = Account(value.username, value.id, value.api_key, value.api_secret)


@app.route('/')
@app.route('/dashboard/')
# visible dashboard which to view and interact
def dashboard():
    return render_template('dashboard.html',
                           accounts=accounts,
                           symbols=SYMBOL_LIST)


@app.route('/account')
# visible dashboard which to view and interact
def account():
    return render_template('account.html',
                           accounts=accounts
                           )


@app.route('/trade_history')
# visible dashboard which to view and interact
def trade_history():
    # trades = []
    # for symbol in SYMBOL_LIST:
    #     trades += user1.exchange.fetch_my_trades(symbol["symbol"])
    #     trades.reverse()
    #
    return render_template('trade_history.html',
                           accounts=accounts,
                           symbols=SYMBOL_LIST)


@app.route('/orders')
def orders():
    # open_orders = []
    # for symbol in SYMBOL_LIST:
    #     open_orders += user1.exchange.fetch_open_orders(symbol['symbol'])
    # open_orders.reverse()
    # btc = user1.exchange.fetch_ticker('BTC/USDT')['close']
    return render_template('orders.html',
                           accounts=accounts)


@app.route('/webhook', methods=['POST'])
# webhook for receiving of orders
def webhook():
    try:
        " capture the webhook through a listener into a variable called webhook_message"
        webhook_message = request.data
        # " parse the text into json format"
        webhook_message = literal_eval(webhook_message.decode('utf8'))  # decoding from bytes to json
        trade_parameters = list(webhook_message.values())
        threads = []
        traders = User.query.filter_by(twopercent=True).all()
        for symbol in SYMBOL_LIST:
            for trader in traders:
                user = Account(name=trader.username,
                               user_id=trader.id,
                               api_k=trader.api_key,
                               api_s=trader.api_secret)
                t1 = threading.Thread(target=user.market_maker, args=(symbol['symbol'],
                                                                      symbol['max_trades'],
                                                                      symbol['premium'],
                                                                      symbol['minimum_trade_size'],
                                                                      trade_parameters,))
                t1.start()
                threads.append(t1)
            user2 = Futures(name='username', user_id=7, api_k='api_key', api_s='api_secret')
            t2 = threading.Thread(target=user2.market_maker,
                                  args=(symbol['symbol'], symbol['max_trades'],
                                        symbol['premium'], symbol['minimum_trade_size'],
                                        trade_parameters,))
            t2.start()
            threads.append(t2)
        for thread in threads:
            thread.join()
        return f"Trade successfully executed"

    except Exception as error:
        print('type is:', error.__class__.__name__)
        print('error occurred,closing database')
        print_exc()
