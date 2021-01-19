# Tradingview_bot
> Automate trading using the alerts webhook on Tradingview. 
---
__Description__
> Captures alerts on the webhook
> These alerts are then parsed and checked for any trade execution paramters 
> After successfully executing the trade, it will immediately place a counter trade
> should a trade be unsuccessful, it will reattempt to submit it again

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
|[ccxt](https://pypi.org/project/ccxt/)|execution of exchange API|
|[Flask](https://pypi.org/project/Flask/)|webhook listener|
|[flask_ngrok](https://pypi.org/project/flask-ngrok/)|tunneling flask through NGROK|
|[NGROK](https://ngrok.com/)|HTTP tunneling|

__Setup requirements:__
- python 3.4 or later
- NGROK
- [Cryptocurrency Trading account](https://www.binance.com/en/register?ref=FGEE7YGZ) <- feel free to use my Binance referral link to score extra 10% off fees
- [tradingview account](https://www.tradingview.com/gopro/?share_your_love=reuben161) <- feel free to use my Tradingview referral link to score extra $30 when signing up for a paid option
- stable internet connection / cloud deployment server
---

__Getting started:__
1. Execute the setup.py file
2. Enter your API_KEY for the exchange you want to trade on
3. Enter your API_SECRET for the exchange you want to trade on
4. Setup will then install all necessary packages
5. Create NGROK account on [NGROK](https://ngrok.com/)
6. Copy paste Tunnel URL with the `/webhook` extension into Tradingview alert
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
