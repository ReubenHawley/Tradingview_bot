from binance.websockets import BinanceSocketManager
from binance.client import Client
import os
from twisted.internet import reactor

try:
    c_dir = os.path.dirname(__file__)
    with open('/home/reuben-laptop/PycharmProjects/Tradingview_bot/config.txt') as key_file:
        api_key, api_secret, _, _ = key_file.read().splitlines()
    client = Client(api_key, api_secret)
    bm = BinanceSocketManager(client)
    # start any sockets here, i.e a trade socket

    def process_message(msg):
        print("message type: {}".format(msg['e']))
        print(msg)
        # do something
    bm.start_user_socket(process_message)
    #conn_key = bm.start_trade_socket('BTCUSDT', process_message)
    # then start the socket manager
    bm.start()
except KeyboardInterrupt:
    reactor.stop()
