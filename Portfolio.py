import pandas as pd


class Portfolio:
    def __init__(self):
        self.columns = ['timestamp', 'orderID', 'symbol', 'price', 'side', 'ordType', 'orderQty']
        self.trade_history = pd.DataFrame(columns=self.columns)

    def ADD_TRADE(self, order):
        try:
            df_length = len(self.trade_history)
            self.trade_history.loc[df_length] = order
        except IndexError:
            print('mismatch in value count being added to the list')
        except Exception as e:
            print(f'error adding trade: {e}')

    def CREATE_CSV(self):
        try:
            self.trade_history.to_csv('portfolio.csv')
        except WindowsError:
            print("windows sucks, move to linux")
        except Exception as e:
            print(f'error creating csv: {e}')
