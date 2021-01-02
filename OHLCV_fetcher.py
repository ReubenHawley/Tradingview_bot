
import time
import pandas as pd
import ccxt  # noqa: E402
from ccxt.base.decimal_to_precision import ROUND_UP  # noqa: E402

# -----------------------------------------------------------------------------
# common constants
def calculate_volatility():
    msec = 1000
    minute = 60 * msec
    hold = 30

    # -----------------------------------------------------------------------------

    exchange = ccxt.binance({
        'rateLimit': 1000,
        'enableRateLimit': True,
        # 'verbose': True,
    })

    limit = 100
    timeframe = "1d"
    interval = exchange.parse_timeframe(timeframe) * 1000
    pair = 'BTC/USDT'
    cols = ['Timestamp', 'open', 'high', 'low', 'close', 'volume']
    while True:

        try:

            print(exchange.milliseconds(), 'Fetching candles')
            since = exchange.round_timeframe(timeframe, exchange.milliseconds(), ROUND_UP) - (limit * interval)
            ohlcv = exchange.fetch_ohlcv(pair, timeframe, since=since, limit=limit)
            df = pd.DataFrame(ohlcv, columns=cols)
            volatility = 100 - abs((df['high'] / df['close']) - (df['low'] / df['close']) * 100)
            volatility = volatility.rolling(9).mean()/2
            print(f'volatility: {float(volatility.tail(1))}')
        except (ccxt.ExchangeError, ccxt.AuthenticationError, ccxt.ExchangeNotAvailable, ccxt.RequestTimeout) as error:

            print('Got an error', type(error).__name__, error.args, ', retrying in', hold, 'seconds...')
            time.sleep(hold)
