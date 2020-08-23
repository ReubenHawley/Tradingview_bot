# Tradingview_bot
An alerts based trade executor

Autobot scans a relevant labeled inbox for alerts from tradingview
these alerts are then checked for any trade execution paramters (AAA + ZZZ)
after successfully executing the trade, you will receive a notification email with the trade details
should a trade be unsuccessful, it will reattempt to submit it again
after execution the alert email is deleted
------------------------------------------------------------------------------------------------------------------------
DISCLAIMER:
trading can lose you money, never trade with money you are not prepared to lose.
Autobot and its creators accept no liability for losses incurred through the usage of this program.
The user uses this program at his/her own risk and by proceeding with setup, installation and usage waives all rights to
claims against its creators, collectively and individually.
------------------------------------------------------------------------------------------------------------------------

Setup requirements:
python 3.4 or later
ccxt
email account with imap enabled and access to 3rd party applications
an inbox labeled incoming_trades
tradingview account(preferably premium) as trade execution orders are placed using alerts


Setup:
execute the setup.py file
enter your API_KEY for the exchange you want to trade on
enter your API_SECRET for the exchange you want to trade on
enter the email address you want to check for alerts
enter your email password for logging in
setup will then install all necessary packages
------------------------------------------------------------------------------------------------------------------------
Executing the bot:
the bot is designed to be left running, errors that have not been handled will be emailed to your address for further inspection
as a safety feature of the bot, you will need to exit it twice, this prevents you from accidentaly stopping the process
------------------------------------------------------------------------------------------------------------------------
executing trades:
Trades are executed via alerts send from tradingview and follow a strict format:

AAA (these are the opening tags to tell our bot to grab all content that folllows
symbol (tell the bot which ticker/symbol to execute a trade on) #CURRENTLY ONLY BTCUSD SUPPORTED#
ordertype (tells the bot if it should execute a limit order or market order)  #CURRENTLY ONLY SUPPORTS MARKET ORDERS#
direction (tells the bot whether to buy or sell) 
size (the amount you wish to trade)
ZZZ (closing tags to tell our bot to grab all content between this and the opening tags
------------------------------------------------------------------------------------------------------------------------
e.g AAA XBTUSD market buy 1 ZZZ
SYMBOLS
symbols should be passed with the \ seperating pairs i.e BTC\USD
symbol is not affected by the casing i.e BTC\USD , btc\usd , BTC\usd these will all be parsed to uppercase
valid parameters(BTCUSD)
------------------------------------------------------------------------------------------------------------------------
ORDERTYPE
ordertype is not affected by the casing i.e market, MARKET, MArKet these will all be parsed to uppercase
valid parameters(MARKET) # CURRENTLY THIS PARAMETER IS UNUSED BUT NEEDS TO BE PASSED AS PART OF ONGOING DEVELOPMENT#
------------------------------------------------------------------------------------------------------------------------
DIRECTION
direction is not affected by the casing i.e buy, SELL, Short these will all be parsed to uppercase
valid parameters(buy,sell,long,short)
------------------------------------------------------------------------------------------------------------------------
SIZE
size must be a number, either integer or floating point decimal
valid parameters(any number value)
------------------------------------------------------------------------------------------------------------------------
