from .account import Account
from termcolor import colored


class Strategy(Account):
    def __init__(self, account):
        super().__init__()
        self.user = account
        self.account = self.user.exchange

    def order_amount(self, symbol, amount, position_type):
        try:
            if position_type == 'relative':
                usdt_amount = (self.user.exchange.fetch_free_balance()['USDT'] / 100) * amount
                positional_amount = float(usdt_amount / self.user.exchange.fetch_ticker(symbol)['close'])
                return positional_amount
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
                order_receipt = self.account.create_order(ticker, trade_type, direction, amount, None)
                return order_receipt
            elif trade_type == "LIMIT":
                print(colored(f'sending order: '
                              f'{ticker} - {trade_type} - {direction} - {amount} - {price}', 'blue'))
                order_receipt = self.account.create_order(ticker, trade_type, direction, amount, price)
                return order_receipt

            if trade_type == "MARKET":
                print(colored(f'sending order on account: '
                              f'{ticker} - {trade_type} - {direction} - {amount} - {None}', 'blue'))
                order_receipt = self.account.create_order(ticker, trade_type, direction, amount, None)
                return order_receipt
            elif trade_type == "LIMIT":
                print(colored(f'sending order: {ticker} - {trade_type} - {direction} - {amount} - {price}', 'blue'))
                order_receipt = self.account.create_order(ticker, trade_type, direction, amount, price)
                return order_receipt

        except Exception as exception:
            print('type is:', exception.__class__.__name__)

    def market_maker(self, trade_symbol, max_trades, premium, webhook_message):
        webhook_message = webhook_message
        base = webhook_message['base']
        quote = webhook_message['quote']
        quantity = float(webhook_message['quantity'])
        side = webhook_message['side']
        symbol = f'{quote}/{base}'
        position_type = webhook_message['position_type']
        amount = self.order_amount(symbol=symbol, amount=quantity, position_type=position_type)
        "do a check to see if the trade is possible"
        if webhook_message is not None:
            if len(self.exchange.fetch_open_orders(trade_symbol)) < max_trades:
                if symbol == trade_symbol:
                    if side == "BUY":
                        if float(amount) * self.account.fetch_ticker(symbol)['close'] < \
                                self.account.fetch_free_balance()[base]:
                            "returns the response from the exchange, whether successful or not"
                            entry_order_response = self.order(ticker=symbol,
                                                              trade_type="MARKET",
                                                              direction="BUY",
                                                              amount=amount,
                                                              price=''
                                                              )

                            "prints response to the console"
                            print(colored(f'entry trade submitted: {entry_order_response}', 'green'))
                            selling_price = entry_order_response['price']*premium
                            if entry_order_response:
                                exit_order_response = self.order(ticker=symbol,
                                                                 trade_type="LIMIT",
                                                                 direction="SELL",
                                                                 amount=amount,
                                                                 price=selling_price
                                                                 )
                                print(colored(f'entry trade submitted: {exit_order_response}', 'green'))
                        else:
                            print(colored("order not submitted, balance insufficient", 'red'))
                    else:
                        print(colored("order not submitted, balance insufficient", 'red'))
                    return '200'
                else:
                    print(f'order received for symbol:{symbol} but strategy is of symbol:{trade_symbol} ')
            else:
                print(f'{max_trades} open trades allowed, current open trades: '
                      f'{len(self.exchange.fetch_open_orders(trade_symbol))}')
        else:
            return "None type received, catching error"

    def __str__(self):
        return f"Strategy for user:{self.user}"
    # takes a strategy as an input and a webhook message for order routing
