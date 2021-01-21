#!/usr/bin/python3
from traceback import print_exc
from flask import Flask, request, render_template
import ccxt
import os
from ast import literal_eval
from flask_ngrok import run_with_ngrok
from Email  import EmailScanner

# Start ngrok when app is run
try:
    " open the config file to retrieve the apikey and secret "
    c_dir = os.path.dirname(__file__)
    with open(os.path.join(c_dir, "config.txt")) as key_file:
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


def order(ticker, trade_type, direction, amount, price):
    try:
        if trade_type == "MARKET":
            print(f'sending order: {ticker} - {trade_type} - {direction} - {amount} - {None}')
            order_receipt = binance.create_order(ticker, trade_type, direction, amount, None)
            return order_receipt
        elif trade_type == "LIMIT":
            print(f'sending order: {ticker} - {trade_type} - {direction} - {amount} - {price}')
            order_receipt = binance.create_order(ticker, trade_type, direction, amount, price)
            return order_receipt
    except Exception as exception:
        email.Send_report(exception.args)
        print('type is:', exception.__class__.__name__)
        print_exc()


# actual web server starts here #
app = Flask(__name__)
run_with_ngrok(app)


@app.route('/')
# visible dashboard which to view and interact
def Dashboard():
    trades = binance.fetch_my_trades('BTC/USDT')
    trades.reverse()
    available_balance = binance.fetch_free_balance()['USDT']
    btc_holdings = binance.fetch_free_balance()['BTC']
    usdt_value_btc_holdings = btc_holdings * binance.fetch_ticker('BTC/USDT')['close']
    total_usdt_value = available_balance + usdt_value_btc_holdings
    return render_template('dashboard.html', trades=trades,
                           usdt_balance=available_balance,
                           btc_holdings=binance.fetch_free_balance()['BTC'],
                           total_usdt_value=total_usdt_value,
                           )


# webhook for receiving of orders
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        " capture the webhook through a listener into a variable called webhook_message"
        webhook_message = request.data
        " parse the text into json format"
        webhook_message = literal_eval(webhook_message.decode('utf8'))  # decoding from bytes to json

        "pass the payload to relevant variables to be executed in the order function"
        base = webhook_message['base']
        quote = webhook_message['quote']
        quantity = float(webhook_message['quantity'])
        order_type = webhook_message['ordertype']
        side = webhook_message['side']
        symbol = f'{quote}/{base}'
        price = webhook_message['price']
        "do a check to see if the trade is possible"
        if side == "BUY":
            if float(webhook_message['quantity'])*binance.fetch_ticker(symbol)['close'] < binance.fetch_free_balance()[base]:
                "returns the response from the exchange, whether successful or not"
                entry_order_response = order(ticker=symbol,
                                             trade_type=order_type,
                                             direction=side,
                                             amount=quantity,
                                             price=price)
                "prints response to the console"
                print(f'entry trade submitted: {entry_order_response}')
                "sends an email of the executed trade"
                email.Send_report(entry_order_response)
            else:
                insufficient_balance = "order not submitted, balance insufficient"
                email.Send_report(insufficient_balance)
                print(insufficient_balance)

        elif side == "SELL":
            if quantity < binance.fetch_free_balance()[quote]:
                print(f"{symbol}-{order_type}-{side}-{quantity}-{price}")
                "returns the response from the exchange, whether successful or not"
                entry_order_response = order(ticker=symbol,
                                             trade_type=order_type,
                                             direction=side,
                                             amount=quantity,
                                             price=price)
                "prints response to the console"
                print(f'entry trade submitted: {entry_order_response}')
                "sends an email of the executed trade"
                email.Send_report(entry_order_response)
            "flask requires a return value otherwise it throws an error"
        else:
            insufficient_balance = "order not submitted, balance insufficient"
            email.Send_report(insufficient_balance)
            print(insufficient_balance)
        return webhook_message
    except Exception as e:
        print('type is:', e.__class__.__name__)
        print_exc()


if __name__ == '__main__':
    "instantiate the flask app in debug mode"
    app.debug = True
    app.run()
