#!/usr/bin/python3
from traceback import print_exc
from flask import Flask, request, render_template
from ast import literal_eval
import os
from flask_ngrok import run_with_ngrok
from python.core.Strategy import Strategy
# Start ngrok when app is run


Reuben = Strategy()

# actual web server starts here #
app = Flask(__name__)
#run_with_ngrok(app)


@app.route('/')
@app.route('/dashboard/')
# visible dashboard which to view and interact
def dashboard():
    trades = Reuben.exchange.fetch_my_trades('BTC/USDT')
    trades.reverse()
    available_balance = Reuben.exchange.fetch_free_balance()['USDT']
    btc_holdings = Reuben.exchange.fetch_free_balance()['BTC']
    usdt_value_btc_holdings = btc_holdings * Reuben.exchange.fetch_ticker('BTC/USDT')['close']
    total_usdt_value = available_balance + usdt_value_btc_holdings
    return render_template('Dashboard.html', trades=trades,
                           usdt_balance=available_balance,
                           btc_holdings=Reuben.exchange.fetch_free_balance()['BTC'],
                           total_usdt_value=total_usdt_value,
                           )


@app.route('/orders')
def orders():
    return render_template('orders.html')


@app.route('/webhook', methods=['POST'])
# webhook for receiving of orders
def webhook():
    try:
        " capture the webhook through a listener into a variable called webhook_message"
        webhook_message = request.data
        " parse the text into json format"
        webhook_message = literal_eval(webhook_message.decode('utf8'))  # decoding from bytes to json
        Reuben.execute(webhook_message)

    except Exception as error:
        print('type is:', error.__class__.__name__)
        print_exc()


if __name__ == '__main__':
    "instantiate the flask app in debug mode"
    app.debug = True
    app.run()
