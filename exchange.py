import ccxt
import os


class Exchange:
    def __init__(self):
        try:
            self.c_dir = os.path.dirname(__file__)
            with open(os.path.join(self.c_dir, "config.txt")) as key_file:
                self.api_key, self.secret, _, _ = key_file.read().splitlines()
            self.binance = ccxt.binance()
            self.binance.apiKey = self.api_key
            self.binance.secret = self.secret
            # self.binance.uid = 'hczj0167'
        except Exception as e:
            print(f'error instantiating exchange: {e}')

    def Fetch_markets(self):
        try:
            markets = self.binance.fetch_markets()
            return markets
        except Exception as e:
            print(f'error in trying to fetch markets: {e}')

    def available_balance(self):
        try:
            account = self.binance.fetchBalance(params={})['free']
            available_balance = (account['BTC'])
            return available_balance
        except Exception as e:
            print(f'error in fetching balance: {e}')

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
        try:
            if symbol == 'XBTUSD':
                symbol = "BTC/USDT"
            if order_type == 'MARKET':
                order = self.market_order(symbol, direction, size)
                return order
            elif order_type == 'LIMIT':
                order = self.limit_order(symbol, direction, size, args)
                return order
        except Exception as e:
            print(f'error in execute trade: {e}')
