import pandas as pd
from read_email import EmailScanner


class Portfolio:
    def __init__(self):
        self.email = EmailScanner()
        self.columns = ['timestamp', 'orderID', 'symbol', 'price', 'side', 'ordType', 'orderQty']
        self.trade_history = pd.DataFrame(columns=self.columns)

    def ADD_TRADE(self, order):
        try:
            df_length = len(self.trade_history)
            self.trade_history.loc[df_length] = order
        except IndexError:
            print('mismatch in value count being added to the list')
        except Exception as e:
            self.email.Send_report(e.args, e)

    def CREATE_CSV(self):
        try:
            self.trade_history.to_csv('portfolio.csv')
        except WindowsError:
            print("windows sucks, move to linux")


if __name__ == '__main__':
    trade_history = Portfolio()
    order = {
        'info': {'orderID': '73da75fe-eff5-d48f-af70-7ecd3c54d079', 'clOrdID': '', 'clOrdLinkID': '', 'account': 694530,
                 'symbol': 'XBTUSD', 'side': 'Sell', 'simpleOrderQty': None, 'orderQty': 1, 'price': 11746,
                 'displayQty': None, 'stopPx': None, 'pegOffsetValue': None, 'pegPriceType': '', 'currency': 'USD',
                 'settlCurrency': 'XBt', 'ordType': 'Market', 'timeInForce': 'ImmediateOrCancel', 'execInst': '',
                 'contingencyType': '', 'exDestination': 'XBME', 'ordStatus': 'Filled', 'triggered': '',
                 'workingIndicator': False, 'ordRejReason': '', 'simpleLeavesQty': None, 'leavesQty': 0,
                 'simpleCumQty': None, 'cumQty': 1, 'avgPx': 11745.5, 'multiLegReportingType': 'SingleSecurity',
                 'text': 'Submitted via API.', 'transactTime': '2020-08-24T18:12:19.141Z',
                 'timestamp': '2020-08-24T18:12:19.141Z'}, 'id': '73da75fe-eff5-d48f-af70-7ecd3c54d079',
        'clientOrderId': '', 'timestamp': 1598292739141, 'datetime': '2020-08-24T18:12:19.141Z',
        'lastTradeTimestamp': 1598292739141, 'symbol': 'BTC/USD', 'type': 'market', 'side': 'sell', 'price': 11746.0,
        'amount': 1.0, 'cost': 11745.5, 'average': 11745.5, 'filled': 1.0, 'remaining': 0.0, 'status': 'closed',
        'fee': None, 'trades': None}
    order_dict = order.pop('info')
    order_details = [order_dict['timestamp'], order_dict['orderID'],
                     order_dict['symbol'], order_dict['price'], order_dict['side'],
                     order_dict['ordType'], order_dict['orderQty']]
    trade_history.ADD_TRADE(order_details)
    trade_history.CREATE_CSV()
    print(order_details[3])
    print(order_details[3]*1.025)
