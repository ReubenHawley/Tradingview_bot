import os
from .Email import EmailScanner
import ccxt


class Account:
    def __init__(self, config="../../config.txt"):
        """Instantiate email client"""
        self.email = EmailScanner()
        """ open the config file to retrieve the apikey and secret 
        instantiate Reuben bot"""
        self.c_dir = os.path.dirname(__file__)
        with open(os.path.join(self.c_dir, config)) as key_file:
            self.api_key, self.secret, _, _ = key_file.read().splitlines()
        "Instantiate the exchange"
        self.exchange = ccxt.binance()
        self.exchange.apiKey = self.api_key
        self.exchange.secret = self.secret


if __name__ == '__main__':
    reuben = Account()
    print(reuben.exchange)
