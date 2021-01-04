from flask import Flask, request, render_template
import ccxt
import os
import pandas as pd
from ast import literal_eval
from Portfolio import Portfolio

try:
    c_dir = os.path.dirname(__file__)
    with open(os.path.join(c_dir, "config.txt")) as key_file:
        api_key, secret, _, _ = key_file.read().splitlines()
    binance = ccxt.binance()
    binance.apiKey = api_key
    binance.secret = secret
    # binance.uid = 'hczj0167'
    Account = Portfolio()
    available_balance = binance.fetch_free_balance()['USDT']
    btc_holdings = binance.fetch_free_balance()['BTC']
    usdt_value_btc_holdings = btc_holdings * binance.fetch_ticker('BTC/USDT')['close']
    total_usdt_value = available_balance + usdt_value_btc_holdings

except Exception as e:
    print(f'error instantiating exchange: {e}')


def order(symbol, order_type, side, quantity, price):
    try:
        print(f'sending order: {symbol} - {order_type} - {side} - {quantity} - {price}')
        order_receipt = binance.create_order(symbol, order_type, side, quantity, price=None)
        return order_receipt
    except Exception as exception:
        print(f"error occurred: {exception.args}")


def exit_all_positions():
    try:
        order('BTC/USDT', "MARKET", "SELL", btc_holdings, price=None)
    except TimeoutError:
        exit_all_positions()


# actual web server starts here #
app = Flask(__name__)


@app.route('/')
# visible dashboard which to view and interact
def Dashboard():
    trades = binance.fetch_my_trades('BTC/USDT')
    trades.reverse()
    return render_template('dashboard.html', trades=trades,
                           usdt_balance=available_balance,
                           btc_holdings=binance.fetch_free_balance()['BTC'],
                           total_usdt_value=total_usdt_value,
                           exit_all_positions=exit_all_positions())

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
        entry_order_response = order(symbol=symbol,
                                     order_type=order_type,
                                     side=side,
                                     quantity=quantity,
                                     price=None)
        if entry_order_response:
            print(f'Trade executed \n{entry_order_response}')
            exit_order_response = order(symbol=symbol,
                                        order_type='LIMIT',
                                        side=side,
                                        quantity=quantity,
                                        price=None)  # TODO change None to limit price
            print(f'Take profit submitted: {exit_order_response}')
        # construct trade details
        trades = binance.fetch_my_trades('BTC/USDT')
        last_trade = trades[-1].pop('info')
        trade = [last_trade['time'],
                 last_trade['orderId'],
                 last_trade['symbol'],
                 last_trade['price'],
                 side,
                 order_type,
                 quantity]
        df = pd.DataFrame(trade)

        # add executed trade to portfolio
        Account.ADD_TRADE(df)
    else:
        webhook_message = None
    return webhook_message
