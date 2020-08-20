import ccxt
import os


class Exchange:
    def __init__(self):
        self.c_dir = os.path.dirname(__file__)
        with open(os.path.join(self.c_dir, "config.txt")) as key_file:
            self.api_key, self.secret, _, _ = key_file.read().splitlines()
        self.bitmex = ccxt.bitmex()
        self.bitmex.apiKey = self.api_key
        self.bitmex.secret = self.secret

    def available_balance(self):
        account = self.bitmex.fetchBalance(params={})['free']
        available_balance = (account['BTC'])
        return available_balance

    def executeTrade(self, symbol, direction, size):
        Long = ['LONG', 'BUY']
        Short = ["SHORT", "SELL"]
        if symbol == 'XBTUSD':
            symbol = "BTC/USD"
        if direction in Long:
            order = self.bitmex.create_market_buy_order(symbol=symbol, amount=size)
            print('Exchange Response:', order)
            return order
        elif direction in Short:
            order = self.bitmex.create_market_sell_order(symbol=symbol, amount=size)
            # returns the response from the exchange
            print('Exchange Response:', order)
            return order
