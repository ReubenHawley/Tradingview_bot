import os
import ccxt
import pandas as pd

class Account:
    def __init__(self, config="../../config.txt"):
        """Instantiate email client"""
        """ open the config file to retrieve the apikey and secret 
        instantiate Reuben bot"""
        self.c_dir = os.path.dirname(__file__)
        with open(os.path.join(self.c_dir, config)) as key_file:
            self.api_key, self.secret, _, _ = key_file.read().splitlines()
        "Instantiate the exchange"
        self.exchange = ccxt.binance()
        self.exchange.apiKey = self.api_key
        self.exchange.secret = self.secret

    def account_holdings(self):
        wallet_holdings = self.exchange.fetch_balance()
        coins = wallet_holdings.pop('info')
        df = pd.DataFrame(coins['balances'])
        df['free'] = df['free'].astype(float)
        df['locked'] = df['locked'].astype(float)
        df = df.loc[(df['free'] > 0.000000)]
        return df.to_html(classes='coin_holdings')

    def outstanding_on_order(self, symbol='BTC/USDT'):
        open_orders = self.exchange.fetch_open_orders(symbol)
        outstanding = 0
        for order in open_orders:
            outstanding += order['remaining']
        close = self.exchange.fetch_ticker(symbol)['close']
        on_order = outstanding * close
        return on_order

    def btc_holdings(self):
        btc_holdings = self.exchange.fetch_free_balance()['BTC']
        on_order = self.outstanding_on_order()
        total = btc_holdings + on_order
        return round(total, 2)

    def account_value(self):
        available_balance = round((self.exchange.fetch_free_balance()['USDT']), 2)
        btc_holdings = self.exchange.fetch_free_balance()['BTC']
        usdt_value_btc_holdings = round((btc_holdings * self.exchange.fetch_ticker('BTC/USDT')['close']), 2)
        on_order = self.outstanding_on_order()
        total_usdt_value = round((available_balance + usdt_value_btc_holdings + on_order), 2)
        return total_usdt_value

    def available_balance(self):
        available_balance = round((self.exchange.fetch_free_balance()['USDT']), 2)
        return available_balance


if __name__ == '__main__':
    reuben = Account()
    wallet = reuben.exchange.fetch_balance()
    coins = wallet.pop('info')
    df = pd.DataFrame(coins['balances'])
    df['free'] = df['free'].astype(float)
    df['locked'] = df['locked'].astype(float)
    df = df.loc[(df['free'] > 0.000000)]
    print(df)
