import ccxt
from termcolor import colored
from py.TV_bot.models import Trade
from py.TV_bot import db


class Account:
    def __init__(self, name, api_k, api_s):
        self.name = name
        """Instantiate email client"""
        """ open the config file to retrieve the apikey and secret 
        instantiate Auto bot"""
        # self.c_dir = os.path.dirname(__file__)
        # with open(os.path.join(self.c_dir, config)) as key_file:
        #     self.api_key, self.secret, _, _ = key_file.read().splitlines()
        "Instantiate the exchange"
        self.exchange = ccxt.binance()
        self.exchange.apiKey = api_k
        self.exchange.secret = api_s
        "instantiate portfolio"
        self.min_trade_size: float = 10

    def account_holdings(self):
        free = self.exchange.fetch_balance()

        coin_holdings = []
        for coin in free['info']['balances']:
            if float(coin['free']) > 0.0:
                coin_holdings.append(coin)
        return coin_holdings

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

    def order_amount(self, symbol, amount, position_type):
        try:
            free = self.exchange.fetch_free_balance()

            if position_type == 'relative':
                if free['USDT'] > 10:
                    usdt_amount = (free['USDT'] / 100) * amount
                    positional_amount = float(usdt_amount / self.exchange.fetch_ticker(symbol)['close'])
                    return positional_amount
                else:
                    print(f"order not submitted for {self.name}, USDT account balance: "
                          f"{free['USDT']}")
                    return None
            elif position_type == 'absolute':
                positional_amount = float(amount)
                return positional_amount
        except TypeError:
            return "wrong value type received, check payload parameters"

    def order(self, ticker, trade_type, direction, amount, price):
        try:
            if trade_type == "MARKET":
                print(colored(f'sending order on account: '
                              f'{ticker} - {trade_type} - {direction} - {amount} - {None}', 'blue'))
                order_receipt = self.exchange.create_order(ticker, trade_type, direction, amount, None)
                return order_receipt
            elif trade_type == "LIMIT":
                print(colored(f'sending order: '
                              f'{ticker} - {trade_type} - {direction} - {amount} - {price}', 'blue'))
                order_receipt = self.exchange.create_order(ticker, trade_type, direction, amount, price)
                return order_receipt

            if trade_type == "MARKET":
                print(colored(f'sending order on account: '
                              f'{ticker} - {trade_type} - {direction} - {amount} - {None}', 'blue'))
                order_receipt = self.exchange.create_order(ticker, trade_type, direction, amount, None)
                return order_receipt
            elif trade_type == "LIMIT":
                print(colored(f'sending order: {ticker} - {trade_type} - {direction} - {amount} - {price}', 'blue'))
                order_receipt = self.exchange.create_order(ticker, trade_type, direction, amount, price)
                return order_receipt

        except Exception as exception:
            print('type is:', exception.__class__.__name__)

    def market_maker(self, trade_symbol, max_trades, premium, min_trade_size, trade_parameters):
        base = trade_parameters[0]
        quote = trade_parameters[1]
        quantity = float(trade_parameters[2])
        side = trade_parameters[3]
        symbol = f'{quote}/{base}'
        position_type = trade_parameters[6]
        amount = self.order_amount(symbol=symbol, amount=quantity, position_type=position_type)
        "do a check to see if the trade is possible"
        try:
            if trade_parameters and amount is not None:
                if len(self.exchange.fetch_open_orders(trade_symbol)) < max_trades:
                    if symbol == trade_symbol:
                        if side == "BUY":
                            if self.exchange.fetch_free_balance()[base] > min_trade_size:
                                if float(amount) * self.exchange.fetch_ticker(symbol)['close'] > min_trade_size:
                                    "returns the response from the exchange, whether successful or not"
                                    entry_order_response = self.exchange.create_market_buy_order(symbol, amount=amount)
                                    entry_trade = Trade(timestamp=entry_order_response['timestamp'],
                                                        symbol=entry_order_response['symbol'],
                                                        side=entry_order_response['side'],
                                                        price=entry_order_response['price'],
                                                        amount=entry_order_response['amount'],
                                                        cost=entry_order_response['cost'],
                                                        fees=entry_order_response['fee']['cost']
                                                        )
                                    db.session.add(entry_trade)
                                    print(colored(f'entry trade submitted to DB for {self.name}: '
                                                  f'{entry_order_response}', 'green'))
                                    selling_price = entry_order_response['price'] * premium
                                    if entry_order_response:
                                        exit_order_response = self.exchange.create_limit_sell_order(symbol,
                                                                                                    entry_order_response[
                                                                                                        'amount'],
                                                                                                    selling_price)
                                        exit_trade = Trade(timestamp=entry_order_response['timestamp'],
                                                           symbol=entry_order_response['symbol'],
                                                           side=entry_order_response['side'],
                                                           price=entry_order_response['price'],
                                                           amount=entry_order_response['amount'],
                                                           cost=entry_order_response['cost'],
                                                           fees=entry_order_response['fee']['cost']
                                                           )
                                        db.session.add(exit_trade)
                                        db.session.commit()
                                        print(colored(f'entry trade submitted for {self.name}: {exit_order_response}',
                                                      'green'))
                                        return '200'
                                else:
                                    print(colored(f"order not submitted, balance insufficient on {self.name}s account",
                                                  'red'))
                        else:
                            print(colored(f"order not submitted for {self.name}, balance insufficient", 'red'))
                        return '200'
                    else:
                        print(
                            f'order received for {self.name} on symbol:{symbol} '
                            f'but strategy is of symbol:{trade_symbol}')
                else:
                    print(f'{max_trades} open trades allowed, current open trades for {self.name}: '
                          f'{len(self.exchange.fetch_open_orders(trade_symbol))}')
            else:
                return "None type received, catching error"
        except Exception as e:
            print(f'Failed to create order for {self.name} with', self.exchange.id, type(e).__name__, str(e))

    def grid_trader(self, trade_symbol, max_trades, trade_parameters):
        premium = 1.01
        min_trade_size: float = 10
        base = trade_parameters[0]
        quote = trade_parameters[1]
        symbol = f'{quote}/{base}'
        position_type = trade_parameters[6]
        amount = round(self.order_amount(symbol=symbol, amount=min_trade_size, position_type=position_type), 2)
        print(amount)
        "do a check to see if the trade is possible"
        try:
            if trade_parameters is not None:
                if len(self.exchange.fetch_open_orders(trade_symbol)) == 0:
                    if float(amount) * self.exchange.fetch_ticker(symbol)['close'] > min_trade_size:
                        "returns the response from the exchange, whether successful or not"
                        entry_order_response = self.exchange.create_market_buy_order(symbol,
                                                                                     amount=amount)
                        trade_data = [entry_order_response['timestamp'],
                                      entry_order_response['symbol'],
                                      entry_order_response['side'],
                                      entry_order_response['price'],
                                      entry_order_response['amount'],
                                      entry_order_response['cost'],
                                      entry_order_response['fee']['cost']
                                      ]
                        print(colored(f'entry trade submitted for {self.name}: {entry_order_response}',
                                      'green'))
                        selling_price = entry_order_response['price'] * premium
                        if entry_order_response:
                            exit_order_response = self.exchange.create_limit_sell_order(symbol,
                                                                                        entry_order_response[
                                                                                            'amount'],
                                                                                        selling_price)
                            print(colored(f'entry trade submitted for {self.name}: {exit_order_response}',
                                          'green'))
                    else:
                        print(colored(f"order not submitted, balance insufficient on {self.name}s account",
                                      'red'))
                    if len(self.exchange.fetch_open_orders(trade_symbol)) < max_trades:
                        if symbol == trade_symbol:
                            if self.exchange.fetch_free_balance()[base] > min_trade_size:
                                if float(amount) * self.exchange.fetch_ticker(symbol)['close'] > min_trade_size:
                                    "returns the response from the exchange, whether successful or not"
                                    entry_order_response = self.exchange.create_market_buy_order(symbol,
                                                                                                 amount=amount)
                                    trade_data = [entry_order_response['timestamp'],
                                                  entry_order_response['symbol'],
                                                  entry_order_response['side'],
                                                  entry_order_response['price'],
                                                  entry_order_response['amount'],
                                                  entry_order_response['cost'],
                                                  entry_order_response['fee']['cost']
                                                  ]
                                    print(colored(f'entry trade submitted for {self.name}: {entry_order_response}',
                                                  'green'))
                                    selling_price = entry_order_response['price'] * premium
                                    if entry_order_response:
                                        exit_order_response = self.exchange.create_limit_sell_order(symbol,
                                                                                                    entry_order_response[
                                                                                                        'amount'],
                                                                                                    selling_price)
                                        print(colored(f'entry trade submitted for {self.name}: {exit_order_response}',
                                                      'green'))
                                else:
                                    print(colored(f"order not submitted, balance insufficient on {self.name}s account",
                                                  'red'))
                            else:
                                print(colored(f"order not submitted for {self.name}, balance insufficient", 'red'))
                            return '200'
                    else:
                        print(f'{max_trades} open trades allowed, current open trades for {self.name}: '
                              f'{len(self.exchange.fetch_open_orders(trade_symbol))}')
                else:
                    return "None type received, catching error"
        except Exception as e:
            print(f'Failed to create order for {self.name} with', self.exchange.id, type(e).__name__, str(e))

    def trendfollower(self, trade_symbol, trade_parameters):
        base = trade_parameters[0]
        quote = trade_parameters[1]
        quantity = float(trade_parameters[2])
        side = trade_parameters[3]
        symbol = f'{quote}/{base}'
        position_type = trade_parameters[6]
        amount = self.order_amount(symbol=symbol, amount=quantity, position_type=position_type)
        "do a check to see if the trade is possible"
        try:
            if trade_parameters and amount is not None:
                if symbol == trade_symbol:
                    if side == "BUY":
                        if self.exchange.fetch_free_balance()[base] > self.min_trade_size:
                            if float(amount) * self.exchange.fetch_ticker(symbol)['close'] > self.min_trade_size:
                                "returns the response from the exchange, whether successful or not"
                                entry_order_response = self.exchange.create_market_buy_order(symbol,
                                                                                             amount=amount)
                                trade_data = [entry_order_response['timestamp'],
                                              entry_order_response['symbol'],
                                              entry_order_response['side'],
                                              entry_order_response['price'],
                                              entry_order_response['amount'],
                                              entry_order_response['cost'],
                                              entry_order_response['fee']['cost']
                                              ]
                                print(colored(f'entry trade submitted for {self.name}: {entry_order_response}',
                                              'green'))

                            else:
                                print(colored(f"order not submitted, balance insufficient on {self.name}s account",
                                              'red'))
                    else:
                        print(colored(f"order not submitted for {self.name}, balance insufficient", 'red'))
                    return '200'
                else:
                    print(
                        f'order received for {self.name} on symbol:{symbol} '
                        f'but strategy is of symbol:{trade_symbol}')
            else:
                return "None type received, catching error"
        except Exception as e:
            print(f'Failed to create order for {self.name} with', self.exchange.id, type(e).__name__, str(e))

    def __str__(self):
        return f"Strategy for {self.name} on exchange: {self.exchange}"
    # takes a strategy as an input and a webhook message for order routing
