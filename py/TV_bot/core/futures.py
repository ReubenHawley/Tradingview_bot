from account import Account
import ccxt
from pprint import pprint


class Futures(Account):
    def __init__(self, name, user_id, api_k, api_s):
        super().__init__(name, user_id, api_k, api_s)
        self.name = name
        self.id = user_id
        """Instantiate email client"""
        """ open the config file to retrieve the apikey and secret 
        instantiate Auto bot"""
        # self.c_dir = os.path.dirname(__file__)
        # with open(os.path.join(self.c_dir, config)) as key_file:
        #     self.api_key, self.secret, _, _ = key_file.read().splitlines()
        "Instantiate the exchange"
        self.exchange = ccxt.binance({
            'enableRateLimit': True,  # https://github.com/ccxt/ccxt/wiki/Manual#rate-limit
            'options': {
                'defaultType': 'future',
                'dualSidePosition': 'false',
                'marginType': 'ISOLATED',
            },
            'apiKey': api_k,
            # https://github.com/ccxt/ccxt/wiki/Manual#authentication
            'secret': api_s,
        })
        "instantiate portfolio"

    def get_trade_mode(self):

        print('Getting your current position mode (One-way or Hedge Mode):')
        response = self.exchange.fapiPrivate_get_positionside_dual()
        if response['dualSidePosition']:
            print('You are in Hedge Mode')
        else:
            print('You are in One-way Mode')

        print('----------------------------------------------------------------------')

    def adjust_position_mode(self,mode):
        if mode == 'one':
            print('Setting your position mode to One-way:')
            response = self.exchange.fapiPrivate_post_positionside_dual({
                'dualSidePosition': False,
            })
            print(response)
        elif mode == 'hedge':
            print('Setting your positions to Hedge mode:')
            response = self.exchange.fapiPrivate_post_positionside_dual({
                'dualSidePosition': True,
            })
            print(response)


    def get_balance(self, symbol):
        self.exchange.load_markets()
        market = self.exchange.market(symbol)  # https://github.com/ccxt/ccxt/wiki/Manual#methods-for-markets-and-currencies
        balance = self.exchange.fetch_balance()  # https://github.com/ccxt/ccxt/wiki/Manual#querying-account-balance

        # https://binance-docs.github.io/apidocs/futures/en/#account-information-user_data

        positions = balance['info']['positions']  # https://github.com/ccxt/ccxt/wiki/Manual#balance-structure
        positions_by_ids = self.exchange.index_by(positions, 'symbol')  # binance's symbol == ccxt's id
        position = self.exchange.safe_value(positions_by_ids, market['id'])
        print('-----------------------------------------')
        pprint(position)
        print('-----------------------------------------')
        print('Your profit and loss for your', symbol, 'position is', position['unrealizedProfit'])

    def position_risk(self):
        markets = self.exchange.load_markets()  # https://github.com/ccxt/ccxt/wiki/Manual#loading-markets
        symbol = 'BTC/USDT'
        market = self.exchange.market(symbol)
        positions = self.exchange.fapiPrivate_get_positionrisk()  # https://github.com/ccxt/ccxt/wiki/Manual#implicit-api-methods
        positions_by_ids = self.exchange.index_by(positions, 'symbol')  # binance's symbol == ccxt's id
        position = self.exchange.safe_value(positions_by_ids, market['id'])

        print('-----------------------------------------')
        pprint(position)
        print('-----------------------------------------')
        print('Your profit and loss for your', symbol, 'position is ', position['unrealizedProfit'])

    def adjust_leverage(self, symbol, leverage:int):
        markets = self.exchange.load_markets()  # https://github.com/ccxt/ccxt/wiki/Manual#loading-markets
        market = self.exchange.market(symbol)  # https://github.com/ccxt/ccxt/wiki/Manual#methods-for-markets-and-currencies

        # https://binance-docs.github.io/apidocs/futures/en/#change-initial-leverage-trade

        self.exchange.fapiPrivate_post_leverage({  # https://github.com/ccxt/ccxt/wiki/Manual#implicit-api-methods
            'symbol': market['id'],  # https://github.com/ccxt/ccxt/wiki/Manual#symbols-and-market-ids
            'leverage': leverage,  # target initial leverage, int from 1 to 125
        })

    def margin_mode(self, mode, symbol):
        markets = self.exchange.load_markets()  # https://github.com/ccxt/ccxt/wiki/Manual#loading-markets
        market = self.exchange.market(symbol)
        if mode == 'isolated':
            print('Changing your', symbol, 'position margin mode to ISOLATED:')
            response = self.exchange.fapiPrivate_post_margintype({
                'symbol': market['id'],
                'marginType': 'ISOLATED',
            })
            print(response)
        elif mode == 'cross':
            print('Changing your', symbol, 'position margin mode to CROSSED:')
            response = self.exchange.fapiPrivate_post_margintype({
                'symbol': market['id'],
                'marginType': 'CROSSED',
            })
            print(response)


    def create_order(self, symbol, order_type, side, amount, price, *args, **kwargs):
        # symbol = 'ETH/BTC'
        # type = 'limit'  # or 'market'
        # side = 'sell'  # or 'buy'
        # amount = 1.0
        # price = 0.060154  # or None

        # extra params and overrides if needed
        params = {
            'positionSide': 'LONG',
            'test': True
        }

        order = self.exchange.create_order(symbol, type, side, amount, price, {
            'type': 'future',
        })

        print(order)


if __name__ == '__main__':
    symbol = "BTC/USDT"
    binance = Futures('dummy',
                      1,
                      'Tvy7itrhTXKdrKPQ0unUTvA4VDlKMDV5WHl8lFmHVZSfxD4OBzPxE0vpmRXZr50V',
                      'S9dl7cJiPoiIC7OTS59HToO9XebDYDYym4JBkUJrf6DbTDpLcJ9xmzhFMG9zr69k')
    binance.get_balance(symbol)
    binance.adjust_position_mode('isolated')
    # binance.create_order(symbol,'LIMIT','BUY',0.001,59500)
    binance.get_balance(symbol)
