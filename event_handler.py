from exchange import Exchange
from read_email import EmailScanner
import time
from Portfolio import Portfolio


if __name__ == '__main__':
    print('Welcome to Autobot:')
    while True:
        try:

            print('connecting to exchange')
            mex = Exchange()
            print('reading executed trades')
            trade_history = Portfolio()
            print('scanning emails')
            read_emails = EmailScanner()
            parameters = read_emails.email_scanner()
            if parameters is not None:
                if mex.available_balance() > 0:  # TODO see if requested trade size !> than available balance
                    order = mex.executeTrade(symbol=parameters[0], direction=parameters[2], size=parameters[3])
                    print(order)
                    if "error" not in order:
                        order_dict = order.pop('info')
                        order_details = [order_dict['timestamp'], order_dict['orderID'],
                                         order_dict['symbol'], order_dict['side'],
                                         order_dict['ordType'], order_dict['orderQty']]
                        trade_history.ADD_TRADE(
                            order_details)  # adds the necessary details from the order to the portfolio
                        trade_history.CREATE_CSV()
                        read_emails.imap.delete_message(read_emails.CountEmails())
                        read_emails.Send_report(order)
                        parameters = None
                        time.sleep(5)
                    else:
                        continue
            else:
                time.sleep(5)
                continue
        except KeyboardInterrupt:
            print("you attempted to stop running the bot, if this was intentional, please exit it again.")
            time.sleep(10)
        except Exception as e:
            print(f"error in processing: {e}")
            read_emails.Send_report(e, f'{e.args}')
            continue
