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

"""TRADE PARAMETERS"""
SYMBOL_LIST = [{"symbol": "BTC/USDT", "max_trades": 100},
               {"symbol": "BNB/USDT", "max_trades": 20}]

# actual web server starts here #
app = Flask(__name__)
run_with_ngrok(app)


@app.route('/')
@app.route('/dashboard/')
# visible dashboard which to view and interact
def dashboard():
    trades = user2.exchange.fetch_my_trades('BTC/USDT')
    trades.reverse()

    return render_template('Dashboard.html', trades=trades)


@app.route('/account')
# visible dashboard which to view and interact
def account():
    return render_template('account.html',
                           usdt_balance=user2.available_balance(),
                           btc_holdings=user2.btc_holdings(),
                           total_usdt_value=user2.account_value(),
                           )


@app.route('/orders')
def orders():
    open_orders = user2.exchange.fetch_open_orders("BTC/USDT")
    open_orders.reverse()
    btc = user2.exchange.fetch_ticker('BTC/USDT')['close']
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
            Thread(target=user2.market_maker, args=(symbol['symbol'], symbol['max_trades'], webhook_message,)).start()
        Thread(target=user1.market_maker, args=("BTC/USDT", 100, webhook_message,)).start()
        return f"Trade successfully executed"

    except Exception as error:
        print('type is:', error.__class__.__name__)
        print_exc()


if __name__ == '__main__':
    "instantiate the flask app in debug mode"
    app.debug = True
    app.run()
