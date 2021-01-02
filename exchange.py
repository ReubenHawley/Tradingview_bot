import ccxt
import os
import pandas as pd
import time
from ccxt.base.decimal_to_precision import ROUND_UP

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

    def Fetch_OHLCV(self, ticker='BTC/USDT', timeframe='1d',number_of_candles=100):
        msec = 1000
        minute = 60 * msec
        hold = 30

        # -----------------------------------------------------------------------------

        exchange = ccxt.binance({
            'rateLimit': 1000,
            'enableRateLimit': True,
            # 'verbose': True,
        })

        limit = number_of_candles
        timeframe = timeframe
        interval = exchange.parse_timeframe(timeframe) * 1000
        pair = ticker
        cols = ['Timestamp', 'open', 'high', 'low', 'close', 'volume']
        try:

            print(exchange.milliseconds(), 'Fetching candles')
            since = exchange.round_timeframe(timeframe, exchange.milliseconds(), ROUND_UP) - (limit * interval)
            ohlcv = exchange.fetch_ohlcv(pair, timeframe, since=since, limit=limit)
            df = pd.DataFrame(ohlcv, columns=cols)
            return df
        except (
        ccxt.ExchangeError, ccxt.AuthenticationError, ccxt.ExchangeNotAvailable, ccxt.RequestTimeout) as error:

            print('Got an error', type(error).__name__, error.args, ', retrying in', hold, 'seconds...')
            time.sleep(hold)

    def Fetch_ticker(self,ticker):
        try:
            return_ticker = self.binance.fetch_ticker(ticker)
            return return_ticker
        except Exception as e:
            print(f'error in trying to fetch markets: {e}')

    def volatility(self,ticker):
        trading_pair = self.Fetch_ticker(ticker)
        volatility = 100 - abs((trading_pair['high']/trading_pair['close']) - (trading_pair['low']/trading_pair['close'])*100)
        return float(volatility)

    def available_balance(self, pair='USDT'):
        try:
            account = self.binance.fetchBalance(params={})['free']
            available_balance = (account[pair])
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
