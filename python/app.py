#!/usr/bin/python3
from traceback import print_exc
from flask import Flask, request, render_template
from ast import literal_eval
from flask_ngrok import run_with_ngrok
from python.core.Strategy import Strategy
from threading import Thread
from python.core.account import Account


""" USER SETTINGS """
user2_config = '../../config.txt'
account2 = Account(user2_config)
user2 = Strategy(account=account2)

user1_config = '../../config_jeroen.txt'
account1 = Account(user1_config)
user1 = Strategy(account=account1)

user3_config = '../../config_reuben.txt'
account3 = Account(user3_config)
user3 = Strategy(account=account3)

"""TRADE PARAMETERS"""
SYMBOL_LIST = [{"symbol": "BTC/USDT", "max_trades": 60},{"symbol": "ETH/USDT", "max_trades": 60},
               {"symbol": "DOT/USDT", "max_trades": 20},{"symbol": "BNB/USDT", "max_trades": 40},
               {"symbol": "OCEAN/USDT", "max_trades": 20},]

# actual web server starts here #
app = Flask(__name__)
run_with_ngrok(app)


@app.route('/')
@app.route('/dashboard/')
# visible dashboard which to view and interact
def dashboard():
    trades = []
    for symbol in SYMBOL_LIST:
        trades += user3.exchange.fetch_my_trades(symbol["symbol"])
    trades.reverse()

    return render_template('Dashboard.html', trades=trades, symbols=SYMBOL_LIST)


@app.route('/account')
# visible dashboard which to view and interact
def account():
    return render_template('account.html',
                           usdt_balance=user3.available_balance(),
                           btc_holdings=user3.btc_holdings(),
                           total_usdt_value=user3.account_value(),
                           )


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
        " parse the text into json format"
        webhook_message = literal_eval(webhook_message.decode('utf8'))  # decoding from bytes to json
        for symbol in SYMBOL_LIST:
            user2.market_maker(symbol['symbol'], symbol['max_trades'], webhook_message)
            user3.market_maker(symbol['symbol'], symbol['max_trades'], webhook_message)
        user1.market_maker('BTC/USDT', 100, webhook_message)
        return f"Trade successfully executed"

    except Exception as error:
        print('type is:', error.__class__.__name__)
        print_exc()


if __name__ == '__main__':
    "instantiate the flask app in debug mode"
    app.debug = True
    app.run()
