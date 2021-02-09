import time
import threading


def order_amount(symbol, trade_type, direction,amount):
    return f'sending order: {symbol} - {trade_type} - {direction} - {amount} - {None}'


def HFT_trader(webhook_message):
    try:
        while True:
            if webhook_message == False:
                t1 = threading.Thread(target=order_amount, args=('btc', 'limit', 'sell', '1',))
                t1.start()
                time.sleep(5)
                continue
            elif webhook_message == True:
                break
    except BlockingIOError:
        print('you fucked shit up again !')

HFT_trader(False)
time.sleep(10)
HFT_trader(True)