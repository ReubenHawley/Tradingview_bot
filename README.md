# Tradingview_bot
> Automate trading using the alerts webhook on tradingview. 
---
__Description__
>Autobot scans a relevant labeled inbox for alerts from tradingview
>these alerts are then checked for any trade execution paramters (AAA + ZZZ)
>after successfully executing the trade, you will receive a notification email with the trade details
>should a trade be unsuccessful, it will reattempt to submit it again
>after execution the alert email is deleted
------------------------------------------------------------------------------------------------------------------------
__DISCLAIMER:__

>trading can lose you money, never trade with money you are not prepared to lose.
>Autobot and its creators accept no liability for losses incurred through the usage of this program.
>The user uses this program at his/her own risk and by proceeding with setup, installation and usage waives all rights to
>claims against its creators, collectively and individually.
------------------------------------------------------------------------------------------------------------------------
__Dependencies:__
|Dependency|purpose|
|----------|-------|
|ccxt|execution of exchange API|
|Flask|webhook listener|
|NGROK|HTTP tunneling|

__Setup requirements:__
- python 3.4 or later
- ccxt
- flask
- tradingview account(preferably premium) as trade execution orders are placed using alerts
- stable internet connection / cloud deployment server
---

__Setup:__
1. execute the setup.py file
2.enter your API_KEY for the exchange you want to trade on
3. enter your API_SECRET for the exchange you want to trade on
4. setup will then install all necessary packages
------------------------------------------------------------------------------------------------------------------------
__Executing the bot:__
> 1. On the commandline/shell `./ngrok http 5000` for a linux or mac, if using windows `reconsider life choices`
> 2. Open seperate terminal or optionally use tmux to create a seperate session
> 3. On the commandline/shell `export FLASK_APP=High_frequency_trader` followed by `export FLASK_ENV=development` and finally `flask run`
------------------------------------------------------------------------------------------------------------------------
__executing trades:__
>Trades are executed via alerts send from tradingview and follow a strict format:

|Parameter|Purpose|Valid Parameters|E.g|
|---------|-------|----------------|---|
|symbol | ticker/symbol to execute a trade on|`str`|"BTC/USDT"|
|Ordertype |execute a limit order or market order|`str`|"MARKET"|
|Direction |buy or sell|`str`|"BUY"|
|size |amount you wish to trade|`float` `int`|1.0008|
```javascript 
{
        "quantity": 0.001,
        "side": "BUY",
        "symbol": "BTC/USDT",
        "ordertype": "MARKET",

}
```
------------------------------------------------------------------------------------------------------------------------
