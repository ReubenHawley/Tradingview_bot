from .account import Account
from .Email import EmailScanner


class Strategy(Account, EmailScanner):
    def __init__(self, account):
        super().__init__()
        self.user = account
        self.account = self.user.exchange
        self.email = EmailScanner()

    def order_amount(self, amount, position_type):
        if position_type == 'relative':
            usdt_amount = (self.user.exchange.fetch_free_balance()['USDT'] / 100) * amount
            positional_amount = float(usdt_amount / self.user.exchange.fetch_ticker("BTC/USDT")['close'])
            print(f"relative trade: {positional_amount}")
            return positional_amount
        elif position_type == 'absolute':
            positional_amount = float(amount)
            print(f"absolute trade: {positional_amount}")
            return positional_amount

    def order(self, ticker, trade_type, direction, amount, price):
        try:
            if trade_type == "MARKET":
                print(f'sending order: {ticker} - {trade_type} - {direction} - {amount} - {None}')
                order_receipt = self.account.create_order(ticker, trade_type, direction, amount, None)
                return order_receipt
            elif trade_type == "LIMIT":
                print(f'sending order: {ticker} - {trade_type} - {direction} - {amount} - {price}')
                order_receipt = self.account.create_order(ticker, trade_type, direction, amount, price)
                return order_receipt

            if trade_type == "MARKET":
                print(f'sending order: {ticker} - {trade_type} - {direction} - {amount} - {None}')
                order_receipt = self.account.create_order(ticker, trade_type, direction, amount, None)
                return order_receipt
            elif trade_type == "LIMIT":
                print(f'sending order: {ticker} - {trade_type} - {direction} - {amount} - {price}')
                order_receipt = self.account.create_order(ticker, trade_type, direction, amount, price)
                return order_receipt

        except Exception as exception:
            self.email.send_report(exception.args)
            print('type is:', exception.__class__.__name__)

    def execute(self, webhook_message):
        """pass the payload to relevant variables to be executed in the order function"""
        base = webhook_message['base']
        quote = webhook_message['quote']
        quantity = float(webhook_message['quantity'])
        order_type = webhook_message['ordertype']
        side = webhook_message['side']
        symbol = f'{quote}/{base}'
        price = webhook_message['price']
        position_type = webhook_message['position_type']
        amount = self.order_amount(quantity, position_type)
        "do a check to see if the trade is possible"
        if webhook_message is not None:
            if side == "BUY":
                if float(amount) * self.account.fetch_ticker(symbol)['close'] < \
                        self.account.fetch_free_balance()[base]:
                    "returns the response from the exchange, whether successful or not"
                    entry_order_response = self.order(ticker=symbol,
                                                      trade_type=order_type,
                                                      direction=side,
                                                      amount=amount,
                                                      price=price
                                                      )

                    "prints response to the console"
                    print(f'entry trade submitted: {entry_order_response}')
                    "sends an email of the executed trade"
                    # self.email.send_report(entry_order_response)

                else:
                    insufficient_balance = "order not submitted, balance insufficient"
                    # self.email.send_report(insufficient_balance)
                    print(insufficient_balance)

            elif side == "SELL":
                if amount < self.account.fetch_free_balance()[quote]:
                    print(f"{symbol}-{order_type}-{side}-{quantity}-{price}")
                    "returns the response from the exchange, whether successful or not"
                    entry_order_response = self.order(ticker=symbol,
                                                      trade_type=order_type,
                                                      direction=side,
                                                      amount=amount,
                                                      price=price
                                                      )

                    "prints response to the console"
                    print(f'entry trade submitted: {entry_order_response}')
                    "sends an email of the executed trade"

            else:
                insufficient_balance = "order not submitted, balance insufficient"
                # self.email.send_report(insufficient_balance)
                print(insufficient_balance)

            return webhook_message
        else:
            return "None type received, catching error"
