import ccxt
import os


class Exchange:
    def __init__(self):
        self.c_dir = os.path.dirname(__file__)
        with open(os.path.join(self.c_dir, "config.txt")) as key_file:
            self.api_key, self.secret, _, _ = key_file.read().splitlines()
        self.binance = ccxt.binance()
        self.binance.apiKey = self.api_key
        self.binance.secret = self.secret
        # self.binance.uid = 'hczj0167'

    def Fetch_markets(self):
        markets = self.binance.fetch_markets()
        return markets

    def available_balance(self):
        account = self.binance.fetchBalance(params={})['free']
        available_balance = (account['BTC'])
        return available_balance

    def limit_order(self, symbol, direction, size, price):
        if direction == 'SELL':
            order = self.binance.create_limit_sell_order(symbol, size, price)
            return order
        elif direction == 'BUY':
            order = self.binance.create_limit_buy_order(symbol, size, price)
            return order

    def market_order(self, symbol, direction, size):
        if direction == 'SELL':
            order = self.binance.create_market_sell_order(symbol, size)
            return order
        elif direction == 'BUY':
            order = self.binance.create_market_buy_order(symbol, size)
            return order

    def executeTrade(self, symbol, order_type, direction, size, *args):
        if symbol == 'BTCUSD':
            symbol = "BTC/USD"
        if order_type == 'MARKET':
            order = self.market_order(symbol, direction, size)
            return order
        elif order_type == 'LIMIT':
            order = self.limit_order(symbol, direction, size, args)
            return order

stamp = Exchange()
print(stamp.Fetch_markets())