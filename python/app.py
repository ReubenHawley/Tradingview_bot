#!/usr/bin/python3
from traceback import print_exc
from flask import Flask, request, render_template
from ast import literal_eval
from flask_ngrok import run_with_ngrok
from python.core.Strategy import Strategy
from threading import Thread


# Start ngrok when app is run
user1_config = '../../config_user1.txt'
user2_config = '../../config.txt'
user2 = Strategy(account=user2_config)
user1 = Strategy(account=user1_config)

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
    available_balance = round((user2.exchange.fetch_free_balance()['USDT']), 2)
    btc_holdings = user2.exchange.fetch_free_balance()['BTC']
    usdt_value_btc_holdings = round((btc_holdings * user2.exchange.fetch_ticker('BTC/USDT')['close']), 2)
    on_order = user2.outstanding_on_order()
    total_usdt_value = round((available_balance + usdt_value_btc_holdings + on_order), 2)
    return render_template('account.html',
                           usdt_balance=available_balance,
                           btc_holdings=user2.exchange.fetch_free_balance()['BTC'],
                           total_usdt_value=total_usdt_value,
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
        response = Thread(target=user2.execute, args=(webhook_message,))
        response.start()
        response2 = Thread(target=user1.execute, args=(webhook_message,))
        response2.start()
        return f"{response}\n {response2}"

    except Exception as error:
        print('type is:', error.__class__.__name__)
        print_exc()


if __name__ == '__main__':
    "instantiate the flask app in debug mode"
    app.debug = True
    app.run()
