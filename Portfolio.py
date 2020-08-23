import pandas as pd
from read_email import EmailScanner


class Portfolio:
    def __init__(self):
        self.email = EmailScanner()
        self.columns = ['timestamp', 'orderID', 'symbol', 'side', 'ordType', 'orderQty']
        self.trade_history = pd.DataFrame(columns=self.columns)

    def ADD_TRADE(self, order):
        try:
            self.trade_history.append(order)
        except IndexError:
            print('mismatch in value count being added to the list')
        except Exception as e:
            self.email.Send_report(e.args, e)

    def CREATE_CSV(self):
        try:
            self.trade_history.to_csv('portfolio.csv')
        except WindowsError:
            print("windows sucks, move to linux")
