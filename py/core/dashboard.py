import os
import csv


class Portfolio:
    def __init__(self, account):
        self.account = account
        self.columns = ['timestamp', 'symbol', 'direction', 'price', 'amount', 'cost', 'fees']
        self.main_dir = os.path.abspath("..")
        self.trade_data_path = 'trade_data/executed_trades.csv'
        self.final_path = os.path.join(self.main_dir, self.trade_data_path)
        self.create_csv()

    def create_csv(self):
        try:  # check if folder exists
            os.stat(os.path.dirname(self.final_path))
        except:  # folder does not exist
            os.makedirs(os.path.dirname(self.final_path))  # create the folder
        headers = ['timestamp', 'symbol', 'direction', 'price', 'amount', 'cost', 'fees']
        with open(self.final_path, mode='w') as output_file:
            csv_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(headers)

    def add_to_csv(self, data):
        with open('../trade_data/executed_trades.csv', mode='a') as output_file:
            csv_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(data)

    def todays_gross_profit(self, symbol):
        since = self.account.exchange.milliseconds() - 86400000  # -1 day from now
        orders = self.account.exchange.fetch_orders(symbol, since, None)
        total_usdt_buys: float = 0
        total_usdt_sells: float = 0
        for order in orders:
            if order['status'] == 'closed':
                if order['side'] == 'buy':
                    total_usdt_buys += order['cost']
                elif order['side'] == 'sell':
                    total_usdt_sells += order['cost']
        residual = total_usdt_buys - total_usdt_sells
        return residual

    def current_avg_entry(self, symbol):
        since = self.account.exchange.milliseconds() - 86400000  # -1 day from now
        orders = self.account.exchange.fetch_open_orders(symbol, since, None)
        total_usdt_buys: float = 0
        for order in orders:
            total_usdt_buys += order['price']
        avg_entry = total_usdt_buys / len(orders)
        return avg_entry

    def current_drawdown(self, symbol):
        avg_entry = self.current_avg_entry(symbol)
        close = self.account.exchange.fetch_ticker(symbol)['close']
        drawdown = 100 - (avg_entry/close)*100
        return drawdown

    def todays_closed_orders(self, symbol):
        if self.account.exchange.has['fetchClosedOrders']:
            since = self.account.exchange.milliseconds() - 86400000  # -1 day from now
            limit = None  # change for your limit
            closed_orders = self.account.exchange.fetch_trades(symbol, since, limit)
            return closed_orders

if __name__ == '__main__':
    entry_order_response = {'info': {'symbol': 'ETHUSDT', 'orderId': 3010491841, 'orderListId': -1, 'clientOrderId': 'QkBryfgKSTg2saUhGDeNtm', 'transactTime': 1613328602642, 'price': '0.00000000', 'origQty': '0.01232000', 'executedQty': '0.01232000', 'cummulativeQuoteQty': '22.24018720', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'MARKET', 'side': 'BUY', 'fills': [{'price': '1805.21000000', 'qty': '0.01232000', 'commission': '0.00012549', 'commissionAsset': 'BNB', 'tradeId': 295609302}]}, 'id': '3010491841', 'clientOrderId': 'QkBryfgKSTg2saUhGDeNtm', 'timestamp': 1613328602642, 'datetime': '2021-02-14T18:50:02.642Z', 'lastTradeTimestamp': None, 'symbol': 'ETH/USDT', 'type': 'market', 'side': 'buy', 'price': 1805.2100000000003, 'amount': 0.01232, 'cost': 22.240187199999998, 'average': 1805.2099999999998, 'filled': 0.01232, 'remaining': 0.0, 'status': 'closed', 'fee': {'cost': 0.00012549, 'currency': 'BNB'}, 'trades': [{'info': {'price': '1805.21000000', 'qty': '0.01232000', 'commission': '0.00012549', 'commissionAsset': 'BNB', 'tradeId': 295609302}, 'timestamp': None, 'datetime': None, 'symbol': 'ETH/USDT', 'id': None, 'order': None, 'type': None, 'side': None, 'takerOrMaker': None, 'price': 1805.21, 'amount': 0.01232, 'cost': 22.240187199999998, 'fee': {'cost': 0.00012549, 'currency': 'BNB'}}]}
    print(entry_order_response['fee']['cost'])