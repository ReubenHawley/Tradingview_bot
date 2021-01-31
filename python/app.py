#!/usr/bin/python3
from traceback import print_exc
from flask import Flask, request, render_template
import ccxt
import os
from ast import literal_eval
from flask_ngrok import run_with_ngrok
from python.core import EmailScanner

# Start ngrok when app is run
try:
    """ open the config file to retrieve the apikey and secret 
    instantiate Reuben bot"""
    c_dir = os.path.dirname(__file__)
    with open(os.path.join(c_dir, "../config.txt")) as key_file:
        api_key, secret, _, _ = key_file.read().splitlines()
    "Instantiate the exchange"
    binance = ccxt.binance()
    binance.apiKey = api_key
    binance.secret = secret

    "Instantiate email client"
    email = EmailScanner()


except Exception as e:
    print('type is:', e.__class__.__name__)
    print_exc()


# actual web server starts here #
app = Flask(__name__)
run_with_ngrok(app)


@app.route('/')
# visible dashboard which to view and interact
def dashboard():
    trades = binance.fetch_my_trades('BTC/USDT')
    trades.reverse()
    available_balance = binance.fetch_free_balance()['USDT']
    btc_holdings = binance.fetch_free_balance()['BTC']
    usdt_value_btc_holdings = btc_holdings * binance.fetch_ticker('BTC/USDT')['close']
    total_usdt_value = available_balance + usdt_value_btc_holdings
    return render_template('Dashboard.html', trades=trades,
                           usdt_balance=available_balance,
                           btc_holdings=binance.fetch_free_balance()['BTC'],
                           total_usdt_value=total_usdt_value,
                           )

@app.route('/orders')
# visible dashboard which to view and interact
def orders():
    return render_template('orders.html',
                           )

# webhook for receiving of orders
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        " capture the webhook through a listener into a variable called webhook_message"
        webhook_message = request.data
        " parse the text into json format"
        webhook_message = literal_eval(webhook_message.decode('utf8'))  # decoding from bytes to json


    except Exception as error:
        print('type is:', error.__class__.__name__)
        print_exc()


if __name__ == '__main__':
    "instantiate the flask app in debug mode"
    app.debug = True
    app.run()
