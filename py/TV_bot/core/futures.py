from ccxt import ExchangeError
from py.TV_bot.core.account import Account
import ccxt
from termcolor import colored
from py.TV_bot.models import Trade
from py.TV_bot import db
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
                'defaultType': 'delivery',
                'dualSidePosition': 'false',
                'adjustForTimeDifference': True,
            },
            'apiKey': api_k,
            # https://github.com/ccxt/ccxt/wiki/Manual#authentication
            'secret': api_s,
        })
        "instantiate portfolio"

    def get_trade_mode(self):

        print('Getting your current position mode (One-way or Hedge Mode):')
        response = self.exchange.dapiPrivate_get_positionside_dual()
        if response['dualSidePosition']:
            print('You are in Hedge Mode')
        else:
            print('You are in One-way Mode')

        print('----------------------------------------------------------------------')

    def adjust_position_mode(self,mode):
        if mode == 'one':
            print('Setting your position mode to One-way:')
            response = self.exchange.dapiPrivate_post_positionside_dual({
                'dualSidePosition': False,
            })
            print(response)
        elif mode == 'hedge':
            print('Setting your positions to Hedge mode:')
            response = self.exchange.dapiPrivate_post_positionside_dual({
                'dualSidePosition': True,
            })
            print(response)

    def get_balance(self, symbol):
        self.exchange.load_markets()
        market = self.exchange.market(symbol)  # https://github.com/ccxt/ccxt/wiki/Manual#methods-for-markets-and-currencies
        balances = self.exchange.dapiPrivate_get_balance()  # https://github.com/ccxt/ccxt/wiki/Manual#querying-account-balance
        return balances

    def get_position(self, symbol):
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
        return position

    def position_risk(self):
        markets = self.exchange.load_markets()  # https://github.com/ccxt/ccxt/wiki/Manual#loading-markets
        symbol = 'BTC/USDT'
        market = self.exchange.market(symbol)
        positions = self.exchange.dapiPrivate_get_positionrisk()  # https://github.com/ccxt/ccxt/wiki/Manual#implicit-api-methods
        positions_by_ids = self.exchange.index_by(positions, 'symbol')  # binance's symbol == ccxt's id
        position = self.exchange.safe_value(positions_by_ids, market['id'])

        print('-----------------------------------------')
        pprint(position)
        print('-----------------------------------------')
        print('Your profit and loss for your', symbol, 'position is ', position['unrealizedProfit'])

    def adjust_leverage(self, symbol, leverage: int):
        markets = self.exchange.load_markets()  # https://github.com/ccxt/ccxt/wiki/Manual#loading-markets
        market = self.exchange.market(symbol)  # https://github.com/ccxt/ccxt/wiki/Manual#methods-for-markets-and-currencies

        # https://binance-docs.github.io/apidocs/futures/en/#change-initial-leverage-trade

        self.exchange.dapiPrivate_post_leverage({  # https://github.com/ccxt/ccxt/wiki/Manual#implicit-api-methods
            'symbol': market['id'],  # https://github.com/ccxt/ccxt/wiki/Manual#symbols-and-market-ids
            'leverage': leverage,  # target initial leverage, int from 1 to 125
        })

    def margin_mode(self, mode, symbol):
        markets = self.exchange.load_markets()  # https://github.com/ccxt/ccxt/wiki/Manual#loading-markets
        market = self.exchange.market(symbol)
        if mode == 'isolated':
            print('Changing your', symbol, 'position margin mode to ISOLATED:')
            response = self.exchange.dapiPrivate_post_margintype({
                'symbol': market['id'],
                'marginType': 'ISOLATED',
            })
            print(response)
        elif mode == 'cross':
            print('Changing your', symbol, 'position margin mode to CROSSED:')
            response = self.exchange.dapiPrivate_post_margintype({
                'symbol': market['id'],
                'marginType': 'CROSSED',
            })
            print(response)

    def transfer_funds(self, amount, coin, account):
        # 1: transfer from spot account to USDT-Ⓜ futures account.
        # 2: transfer from USDT-Ⓜ futures account to spot account.
        # 3: transfer from spot account to COIN-Ⓜ futures account.
        # 4: transfer from COIN-Ⓜ futures account to spot account.
        # code = 'USDT'
        # amount = 123.45
        currency = self.exchange.currency(coin)

        print('Moving', coin, 'funds from your spot account to your futures account:')

        response = self.exchange.sapi_post_futures_transfer({
            'asset': currency['id'],
            'amount': self.exchange.currency_to_precision(coin, amount),
            'type': account,
        })

    def adjust_margin(self,symbol, position_side:str,amount, margin_type:int):
        # position_side = BOTH for One-way positions, LONG or SHORT for Hedge Mode
        # margin_type = 1:  add position margin, 2:  reduce position margin

        markets = self.exchange.load_markets()  # https://github.com/ccxt/ccxt/wiki/Manual#loading-markets
        market = self.exchange.market(symbol)
        print('Modifying your ISOLATED', symbol, 'position margin:')
        response = self.exchange.dapiPrivate_post_positionmargin({
            'symbol': market['id'],
            'amount': amount,  # ←-------------- YOUR AMOUNT HERE
            'positionSide': position_side,
            'type': margin_type,
        })

        print('----------------------------------------------------------------------')

    def create_limit_order(self, symbol, price, side, amount, *args, **kwargs):
        try:
            self.exchange.load_markets()  # preload markets first
            market = self.exchange.markets[symbol]  # get the market by a unified symbol
            response = self.exchange.create_limit_order(symbol=symbol,
                                                        side=side,
                                                        amount=amount,
                                                        price=price,
                                                        params=kwargs)
            return response
        except ExchangeError as e:
            print(e)

    def create_market_order(self, symbol, side, amount, *args, **kwargs):
        try:
            self.exchange.load_markets()  # preload markets first
            market = self.exchange.markets[symbol]  # get the market by a unified symbol
            response = self.exchange.create_market_order(symbol=symbol,
                                                         side=side,
                                                         amount=amount,
                                                         price=None,
                                                         params=kwargs)
            return response
        except ExchangeError as e:
            print(e)

    def market_maker(self, trade_symbol, max_trades, premium, min_trade_size, trade_parameters):
        base = trade_parameters[0]
        quote = trade_parameters[1]
        symbol = "BTC/USD" #f'{quote}/{base}'

        "do a check to see if the trade is possible"
        try:
            if trade_parameters is not None:
                if symbol == trade_symbol:
                    "returns the response from the exchange, whether successful or not"
                    entry_order_response = self.create_market_order(symbol=symbol, side="BUY", amount=1)
                    order_data = self.exchange.fetch_order(id=entry_order_response['info']['orderId'], symbol=symbol)
                    # entry_trade = Trade(timestamp=entry_order_response['timestamp'],
                    #                     symbol=entry_order_response['symbol'],
                    #                     side=entry_order_response['side'],
                    #                     price=float(order_data['info']['avgPrice']),
                    #                     amount=entry_order_response['amount'],
                    #                     cost=entry_order_response['cost'],
                    #                     fees=entry_order_response['fee']['cost'],
                    #                     user_id=self.id
                    #                     )
                    # db.session.add(entry_trade)
                    print(colored(f'entry trade submitted to DB for {self.name}: ', 'white'))
                    print(colored(f'{entry_order_response}', 'green'))
                    selling_price = float(order_data['info']['avgPrice']) * premium
                    if entry_order_response:
                        exit_order_response = \
                            self.exchange.create_limit_order(symbol=symbol,
                                                             side="SELL",
                                                             amount=1,
                                                             price=selling_price)
                        self.adjust_margin(symbol=symbol, position_side='BOTH', amount=0.0017, margin_type=1)
                        print('adjusting margin for account')
                        # exit_trade = Trade(timestamp=entry_order_response['timestamp'],
                        #                    symbol=entry_order_response['symbol'],
                        #                    side=entry_order_response['side'],
                        #                    price=selling_price,
                        #                    amount=entry_order_response['amount'],
                        #                    cost=entry_order_response['cost'],
                        #                    fees=entry_order_response['fee']['cost'],
                        #                    user_id=self.id
                        #                    )
                        # db.session.add(exit_trade)
                        # db.session.commit()
                        print(colored(f'entry trade submitted for {self.name}: {exit_order_response}',
                                      'green'))
                        return '200'
                else:
                    print(
                        f'order received for {self.name} on symbol:{symbol} '
                        f'but strategy is of symbol:{trade_symbol}')
            else:
                return "None type received, catching error"
        except Exception as e:
            print(f'Failed to create order for {self.name} with', self.exchange.id, type(e).__name__, str(e))


