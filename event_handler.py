from exchange import Exchange
from read_email import EmailScanner
from time import time, sleep
from Portfolio import Portfolio
import sys
import ccxt


if __name__ == '__main__':
    print('Welcome to Autobot:')
    while True:
        try:
            print('connecting to exchange')
            # mex = Exchange()
            print('reading executed trades')
            trade_history = Portfolio()
            print('scanning emails')
            read_emails = EmailScanner()
            parameters = read_emails.email_scanner()
            if parameters is not None:
                if 1 == 1:  #mex.available_balance() > 0:  # TODO see if requested trade size !> than available balance
                    # order = mex.executeTrade(parameters[0], parameters[1],parameters[2], parameters[3])
                    # simulating the order as it is received and the response
                    binance = ccxt.binance()
                    ticker = binance.fetch_ticker(symbol='BTC/USDT')

                    entry_order = {
                        'timestamp': round(time()),
                        'orderID': round(time()),
                        'symbol': parameters[0],
                        'price':ticker['close'],
                        'side': parameters[2],
                        'ordType': parameters[1],
                        'orderQty': parameters[3]
                    }
                    print(entry_order)
                    if "error" not in entry_order:
                        read_emails.Send_report(entry_order)
                        read_emails.imap.delete_message(read_emails.CountEmails())
                        order_dict = entry_order  # temp removal of order.pop('info')
                        order_details = [order_dict['timestamp'], order_dict['orderID'],
                                         order_dict['symbol'], order_dict['price'], order_dict['side'],
                                         order_dict['ordType'], order_dict['orderQty']]
                        trade_history.ADD_TRADE(order_details)  # adds the order to the portfolio
                        trade_history.CREATE_CSV()
                        sell_price = order_details[3]*1.025
                        # exit_order = mex.executeTrade(parameters[0], 'LIMIT', 'SELL',parameters[3], sell_price)
                        exit_order = {
                            'timestamp': round(time()),
                            'orderID': round(time()),
                            'symbol': parameters[0],
                            'price': sell_price,
                            'side': 'sell',
                            'ordType': 'limit',
                            'orderQty': parameters[3]
                        }
                        trade_history.ADD_TRADE(exit_order)  # adds the order to the portfolio
                        trade_history.CREATE_CSV()
                        print(exit_order)
                        read_emails.Send_report(exit_order)
                        parameters = None
                        sleep(5)
                    else:
                        print('error encountered, retrying')
                        continue
            else:
                sleep(5)
                continue
        except KeyboardInterrupt:
            print("you attempted to stop running the bot, if this was intentional, please exit it again.")
            sleep(10)
        except:
            e = sys.exc_info()[0]
            print("<p>Error: %s</p>" % e)
            #read_emails.Send_report(e, f'{e.args}')
            continue
