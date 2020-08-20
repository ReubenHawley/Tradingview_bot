from exchange import Exchange
from read_email import EmailScanner
import time


if __name__ == '__main__':
    print('Welcome to Autobot:')
    while True:
        try:

            print('connecting to exchange')
            mex = Exchange()
            print('scanning emails')
            read_emails = EmailScanner()
            parameters = read_emails.email_scanner()
            if parameters is not None:
                if mex.available_balance() > 0:  # TODO see if requested trade size !> than available balance
                    order = mex.executeTrade(symbol=parameters[0], direction=parameters[2], size=parameters[3])
                    print(type(order))
                    if "error" not in order:
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
