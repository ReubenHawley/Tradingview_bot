# from exchange import Exchange
from read_email import EmailScanner
from time import time, sleep
from Portfolio import Portfolio
import sys
import ccxt
from exchange import Exchange
global exit_order
from OHLCV_fetcher import calculate_volatility

print('Welcome to Autobot:')
print('connecting to exchange')
binance = Exchange()
open_entry_order_list = []
open_exit_order_list = []
print('creating portfolio of trades')
#trade_history = Portfolio()
print('portfolio created')
while True:
    try:
        print('connecting to exchange')
        print('reading executed trades')
        print('scanning emails')
        read_emails = EmailScanner()
        parameters = read_emails.email_scanner()
        print(parameters)
        free_balance = binance.available_balance() # checking available balance
        if parameters is not None:
            if parameters[3] < free_balance: # check to see if funds are available for the trade
                order = binance.executeTrade(parameters[0], parameters[1],parameters[2], parameters[3])
                print(order)
                # simulating the order as it is received and the response
                ticker = binance.Fetch_OHLCV()['close']  # fetch the latest symbol price
                print(ticker)
                entry_order = {
                    'timestamp': round(time()),
                    'orderID': round(time()),
                    'symbol': parameters[0],
                    'price': ticker['close'],
                    'side': parameters[2],
                    'ordType': parameters[1],
                    'orderQty': parameters[3]
                }
                print(f'executed trade: \n{entry_order}')
                if "error" not in entry_order:
                    read_emails.Send_report(entry_order)
                    read_emails.imap.delete_message(read_emails.CountEmails())  # delete order from emails
                    order_dict = entry_order  # temp removal of order.pop('info')
                    order_details = [order_dict['timestamp'], order_dict['orderID'],
                                     order_dict['symbol'], order_dict['price'], order_dict['side'],
                                     order_dict['ordType'], order_dict['orderQty']]
                    trade_history.ADD_TRADE(order_details)  # adds the order to the portfolio
                    open_entry_order_list.append(float(order_dict['price']))
                    trade_history.CREATE_CSV()
                    sell_price = order_details[3]* (1+(calculate_volatility()/100))  #TODO change to volatility rate
                    sellQTY = float(order_dict['orderQty'])*(1+(calculate_volatility()/100)) #TODO change to volatility rate
                    exit_order = binance.executeTrade(parameters[0], 'LIMIT', 'SELL', parameters[3], sell_price)
                    exit_order = {
                        'timestamp': round(time()),
                        'orderID': round(time()),
                        'symbol': parameters[0],
                        'price': sell_price,
                        'side': 'sell',
                        'ordType': 'limit',
                        'orderQty': sellQTY
                    }
                    print(f'submitted exit order:\n{exit_order}')
                    open_exit_order_list.append(float(exit_order['price']))
                    parameters = None
                    entry_order = None
                    order_dict = None
                    order_details = None
                    sleep(5)
                else:
                    print('error encountered, retrying')
                    continue
        if open_exit_order_list is not None:
            for key, placed_exit_order in enumerate(open_exit_order_list):
                ticker = binance.fetch_ticker(symbol='BTC/USDT')
                if ticker['close'] > placed_exit_order:
                    trade_history.ADD_TRADE(exit_order)  # adds the order to the portfolio
                    read_emails.Send_report(exit_order)
                    open_entry_order_list.__delitem__(key)
                    open_exit_order_list.__delitem__(key)
                    exit_order = None
        else:
            sleep(5)
            continue
    except KeyboardInterrupt:
        print("you attempted to stop running the bot, if this was intentional, please exit it again.")
        sleep(10)
    except:
        e = sys.exc_info()[0]
        print("Error: %s" % e)
        # read_emails.Send_report(e, f'{e.args}')
        continue
