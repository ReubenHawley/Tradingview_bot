from flask import Flask, request, render_template
import ccxt
import os
from ast import literal_eval
from flask_ngrok import run_with_ngrok

# Start ngrok when app is run
try:
    c_dir = os.path.dirname(__file__)
    with open(os.path.join(c_dir, "config.txt")) as key_file:
        api_key, secret, _, _ = key_file.read().splitlines()
    binance = ccxt.binance()
    binance.apiKey = api_key
    binance.secret = secret
    # binance.uid = 'hczj0167'
    available_balance = binance.fetch_free_balance()['USDT']
    btc_holdings = binance.fetch_free_balance()['BTC']
    usdt_value_btc_holdings = btc_holdings * binance.fetch_ticker('BTC/USDT')['close']
    total_usdt_value = available_balance + usdt_value_btc_holdings

except Exception as e:
    print(f'error instantiating exchange: {e}')


def order(ticker, trade_type, direction, amount, price):
    try:
        print(f'sending order: {ticker} - {trade_type} - {direction} - {amount} - {price}')
        order_receipt = binance.create_order(ticker, trade_type, direction, amount, price)
        return order_receipt
    except Exception as exception:
        print(f"error occurred: {exception.args}")


# actual web server starts here #
app = Flask(__name__)
run_with_ngrok(app)


@app.route('/')
# visible dashboard which to view and interact
def Dashboard():
    trades = binance.fetch_my_trades('BTC/USDT')
    trades.reverse()
    return render_template('dashboard.html', trades=trades,
                           usdt_balance=available_balance,
                           btc_holdings=binance.fetch_free_balance()['BTC'],
                           total_usdt_value=total_usdt_value,
                           )

# webhook for receiving of orders


@app.route('/webhook', methods=['POST'])
def webhook():
    webhook_message = request.data
    webhook_message = literal_eval(webhook_message.decode('utf8'))  # decoding from bytes to json

    # defining the order criteria
    quantity = webhook_message['quantity']
    order_type = webhook_message['ordertype']
    side = webhook_message['side']
    symbol = webhook_message['symbol']
    close = binance.fetch_ticker('BTC/USDT')['close']
    position_size = close*quantity

    # do a check to see if the trade is possible
    if position_size < available_balance:
        entry_order_response = order(ticker=symbol,
                                     trade_type=order_type,
                                     direction=side,
                                     amount=quantity,
                                     price=None)
        print(f'entry trade submitted: {entry_order_response}')

        if entry_order_response:
            limit_price = round(float(close * 1.003), 2)
            sell = "SELL"
            exit_order_response = order(ticker=symbol,
                                        trade_type='LIMIT',
                                        direction=sell,
                                        amount=quantity,
                                        price=limit_price)  # TODO change None to limit price"""
            if exit_order_response:
                print(f'Take profit submitted: {exit_order_response}')
    return webhook_message

if __name__ == '__main__':
    app.debug = True
    app.run()
