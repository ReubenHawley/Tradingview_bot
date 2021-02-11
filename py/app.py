#!/usr/bin/python3
from traceback import print_exc
from flask import Flask, request, render_template
from ast import literal_eval
from flask_ngrok import run_with_ngrok
import threading
from py.core.Strategy import Strategy
from py.core.account import Account

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
SYMBOL_LIST = [{"symbol": "BTC/USDT", "max_trades": 60, 'premium': 1.02},
               {"symbol": "ETH/USDT", "max_trades": 60, 'premium': 1.02},
               {"symbol": "DOT/USDT", "max_trades": 20, 'premium': 1.02},
               {"symbol": "BNB/USDT", "max_trades": 40, 'premium': 1.02},
               {"symbol": "OCEAN/USDT", "max_trades": 20, 'premium': 1.02}]

# actual web server starts here #
app = Flask(__name__)
run_with_ngrok(app)


@app.route('/')
@app.route('/dashboard/')
# visible dashboard which to view and interact
def dashboard():
    trades = []
    for symbol in SYMBOL_LIST:
        trades += user2.exchange.fetch_my_trades(symbol["symbol"])
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
        print(webhook_message)
        # " parse the text into json format"
        webhook_message = literal_eval(webhook_message.decode('utf8'))  # decoding from bytes to json
        trade_parameters = list(webhook_message.values())
        threads = []
        for symbol in SYMBOL_LIST:
            t1 = threading.Thread(target=user2.market_maker, args=(symbol['symbol'],
                                                                   symbol['max_trades'],
                                                                   symbol['premium'],
                                                                   trade_parameters,))
            t1.start()
            threads.append(t1)
            t2 = threading.Thread(target=user1.market_maker, args=(symbol['symbol'],
                                                                   symbol['max_trades'],
                                                                   symbol['premium'],
                                                                   webhook_message,))
            t2.start()

            threads.append(t2)
        t3 = threading.Thread(target=user1.market_maker, args=(SYMBOL_LIST[0]['symbol'],
                                                               SYMBOL_LIST[0]['max_trades'],
                                                               SYMBOL_LIST[0]['premium'],
                                                               webhook_message,))
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
