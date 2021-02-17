import sqlite3
import ccxt


"instantiate database"
connection = sqlite3.connect('tvBot.db')
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS crypto (
        id INTEGER PRIMARY KEY, 
        ticker TEXT NOT NULL UNIQUE, 
        base TEXT NOT NULL,
        quote TEXT NOT NULL,
        symbol TEXT NOT NULL,
        min_notional REAL NOT NULL
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS coin_price (
        id INTEGER PRIMARY KEY, 
        crypto_id INTEGER,
        date NOT NULL,
        open NOT NULL, 
        high NOT NULL, 
        low NOT NULL, 
        close NOT NULL, 
        adjusted_close NOT NULL, 
        volume NOT NULL,
        FOREIGN KEY (crypto_id) REFERENCES crypto (id)
    )
""")

binance = ccxt.binance()
markets = binance.fetch_markets()
for market in markets:
    if 'USDT' in market['id']:
        print(market['filters'])
        #cursor.execute("INSERT INTO stock (ticker, base, quote, symbol, min_notional ) VALUES (?,?,?,?,?)",
        # (market['id'], market['base'], market['quote'], market['symbol']))

connection.commit()