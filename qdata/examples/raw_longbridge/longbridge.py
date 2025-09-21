from longport.openapi import TradeContext, Config
from time import sleep
from longport.openapi import QuoteContext, Config, SubType, PushQuote


    

config = Config(app_key = "xx", app_secret = "xx", 
                access_token = "xx")

ctx = TradeContext(config)

resp = ctx.account_balance()
print(resp)

def on_quote(symbol: str, quote: PushQuote):
    print(symbol, quote)
    
ctx = QuoteContext(config)
ctx.set_on_quote(on_quote)
symbols = ["700.HK"]
ctx.subscribe(symbols, [SubType.Quote], True)
sleep(30)