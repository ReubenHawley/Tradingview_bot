import os
import csv


class Portfolio:
    def __init__(self, account):
        self.account = account
        self.columns = ['timestamp', 'symbol', 'direction', 'price', 'amount', 'cost', 'fees']
        self.main_dir = os.path.abspath("../..")
        self.trade_data_path = f'trade_data/{self.account.name}executed_trades.csv'
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
        since = self.account.milliseconds() - 86400000  # -1 day from now
        orders = self.account.fetch_orders(symbol, since, None)
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
        since = self.account.milliseconds() - 86400000  # -1 day from now
        orders = self.account.fetch_open_orders(symbol, since, None)
        total_usdt_buys: float = 0
        for order in orders:
            total_usdt_buys += order['price']
        avg_entry = total_usdt_buys / len(orders)
        return avg_entry

    def current_drawdown(self, symbol):
        avg_entry = self.current_avg_entry(symbol)
        close = self.account.fetch_ticker(symbol)['close']
        drawdown = 100 - (avg_entry/close)*100
        return drawdown

    def todays_closed_orders(self, symbol):
        if self.account.exchange.has['fetchClosedOrders']:
            since = self.account.exchange.milliseconds() - 86400000  # -1 day from now
            limit = None  # change for your limit
            closed_orders = self.account.exchange.fetch_trades(symbol, since, limit)
            return closed_orders
