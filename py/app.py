#!/usr/bin/python3
from traceback import print_exc
from flask import Flask, request, render_template
from ast import literal_eval
from flask_ngrok import run_with_ngrok
import threading
from py.core.account import Account
import os
script_dir = os.path.abspath("..")


""" USER SETTINGS """
user2_config = f'{script_dir}/config.txt'
user2 = Account(name='chris', config=user2_config)


user1_config = f'{script_dir}/config_jeroen.txt'
user1 = Account(name='jeroen', config=user1_config)

user3_config = f'{script_dir}/config_reuben.txt'
user3 = Account(name='Willem', config=user3_config)


"""TRADE PARAMETERS"""
SYMBOL_LIST = [{"symbol": "BTC/USDT", "max_trades": 120, 'premium': 1.005, 'minimum_trade_size': 10},
               {"symbol": "ETH/USDT", "max_trades": 120, 'premium': 1.005, 'minimum_trade_size': 10},
                {"symbol": "BNB/USDT", "max_trades": 80, 'premium': 1.005, 'minimum_trade_size': 10},
               {"symbol": "DOT/USDT", "max_trades": 40, 'premium': 1.005, 'minimum_trade_size': 10},
                {"symbol": "CRV/USDT", "max_trades": 40, 'premium': 1.005, 'minimum_trade_size': 10},
               {"symbol": "OCEAN/USDT", "max_trades": 40, 'premium': 1.005, 'minimum_trade_size': 10}]

# actual web server starts here #
app = Flask(__name__)
run_with_ngrok(app)


@app.route('/')
@app.route('/dashboard/')
# visible dashboard which to view and interact
def dashboard():
    return render_template('dashboard.html', symbols=SYMBOL_LIST)


@app.route('/account')
# visible dashboard which to view and interact
def account():
    return render_template('account.html',
                           usdt_balance=user3.available_balance(),
                           btc_holdings=user3.btc_holdings(),
                           total_usdt_value=user3.account_value(),
                           coins=user3.account_holdings(),
                           )


@app.route('/trade_history')
# visible dashboard which to view and interact
def trade_history():
    trades = []
    for symbol in SYMBOL_LIST:
        trades += user2.exchange.fetch_my_trades(symbol["symbol"])
        trades.reverse()

    return render_template('trade_history.html', trades=trades, symbols=SYMBOL_LIST)


@app.route('/orders')
def orders():
    open_orders = []
    for symbol in SYMBOL_LIST:
        open_orders += user3.exchange.fetch_open_orders(symbol['symbol'])
    open_orders.reverse()
    btc = user3.exchange.fetch_ticker('BTC/USDT')['close']
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
        threads = []
        for symbol in SYMBOL_LIST:
            t1 = threading.Thread(target=user2.market_maker, args=(symbol['symbol'],
                                                                   symbol['max_trades'],
                                                                   symbol['premium'],
                                                                   symbol['minimum_trade_size'],
                                                                   trade_parameters,))
            t1.start()
            threads.append(t1)
            t2 = threading.Thread(target=user3.market_maker, args=(symbol['symbol'],
                                                                   symbol['max_trades'],
                                                                   symbol['premium'],
                                                                   symbol['minimum_trade_size'],
                                                                   trade_parameters,))
            t2.start()

            threads.append(t2)
        t3 = threading.Thread(target=user1.market_maker, args=(SYMBOL_LIST[0]['symbol'],
                                                               SYMBOL_LIST[0]['max_trades'],
                                                               SYMBOL_LIST[0]['premium'],
                                                               SYMBOL_LIST[0]['minimum_trade_size'],
                                                               trade_parameters,))
        t3.start()
        threads.append(t3)
        for thread in threads:
            thread.join()
        return f"Trade successfully executed"

    except Exception as error:
        print('type is:', error.__class__.__name__)
        print_exc()


if __name__ == '__main__':
    "instantiate the flask app in debug mode"
    app.debug = True
    app.run()
