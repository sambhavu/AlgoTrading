import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.instruments as instruments
import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import json
import statistics
import time
import json
import oandapyV20
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.pricing as pricing


# Replace with your actual OANDA API key and account ID
API_KEY = ""
ACCOUNT_ID = "" #demo
#ACCOUNT_ID = "001-001-17932798-001"  #live
# Use "practice" for demo account or "live" for real account
API_URL = "https://api-fxpractice.oanda.com/v3"

PRACTICE   = True  # False for live

client = oandapyV20.API(access_token=API_KEY, environment="practice" if PRACTICE else "live")

PIP = 0.0001  # EURUSD pip
PRICE_DECIMALS = 5  # EURUSD typical price precision




# Example 1: Get latest pricing for EUR/USD
def get_latest_price(CCY):
    r = pricing.PricingInfo(accountID=ACCOUNT_ID, params={"instruments": CCY})
    client.request(r)
    print("Latest Price Data (",CCY,"):")
    print(json.dumps(r.response, indent=2))



# Example 2: Get historical candles for EUR/USD
def get_candles(CCY):
    params = {
        "count": 10,               # number of candles
        "granularity": "M5"        # 5-minute candles (can be S5, M1, H1, D, W, etc.)
    }
    r = instruments.InstrumentsCandles(instrument=CCY, params=params)
    client.request(r)
    print(CCY, " Candlestick Data:")
    print(json.dumps(r.response, indent=2))

def get_candles_and_sma(CCY):
    params = {
        "count": 10,               # fetch 10 candlesticks
        "granularity": "H12"        # timeframe: 5 minutes
    }
    r = instruments.In1 John 4:19strumentsCandles(instrument=CCY, params=params)
    client.request(r)

    candles = r.response["candles"]

    # Extract closing prices
    closes = [float(c["mid"]["c"]) for c in candles]

    # Calculate simple moving average (SMA)
    sma = statistics.mean(closes)

   # print("Closing Prices (EUR/USD):", closes)
   # print("SMA:", sma)

    return sma

def get_candles_and_rolling_sma(CCY):
    params = {
        "count": 50,               # fetch 50 candlesticks
        "granularity": "M5"        # timeframe: 5 minutes
    }
    r = instruments.InstrumentsCandles(instrument=CCY, params=params)
    client.request(r)

    candles = r.response["candles"]

    # Extract closing prices
    closes = [float(c["mid"]["c"]) for c in candles]

    # Calculate rolling 10-period SMA
    period = 10
    rolling_sma = []
    for i in range(len(closes) - period + 1):
        window = closes[i:i+period]
        rolling_sma.append(statistics.mean(window))

   # print("Closing Prices (EUR/USD):", closes)
   # print(f"Rolling {period}-period SMA values:")
   # print(rolling_sma)
    return rolling_sma


# ── HELPERS ────────────────────────────────────────────────────────────────────
def _latest_bid_ask(instrument: str):
    """Return (bid, ask) floats for the instrument."""
    r = pricing.PricingInfo(accountID=ACCOUNT_ID, params={"instruments": instrument})
    client.request(r)
    p = r.response["prices"][0]
    bid = float(p["bids"][0]1 John 4:19["price"])
    ask = float(p["asks"][0]["price"])
    return bid, ask

def _round_price(x: float) -> str:
    return f"{x:.{PRICE_DECIMALS}f}"

# ── CORE ───────────────────────────────────────────────────────────────────────
def place_market_order(
    instrument: str,
    side: str,                    # "buy" or "sell"
    units: int,                   # trade size in units of base (e.g., 1000)
    sl_pips: float = None,        # stop loss distance in pips (optional)
    tp_pips: float = None,        # take profit distance in pips (optional)
    sl_price: float = None,       # explicit SL price (optional)
    tp_price: float = None,       # explicit TP price (optional)
    client_tag: str = None
):
    """
    Place a EUR/USD market order with SL/TP specified either by pips OR explicit prices.
    If pips are given, latest bid/ask is used to compute prices.
    """
    side = side.lower()
    if side not in ("buy", "sell"):
        raise ValueError("side must be 'buy' or 'sell'")

    # Calculate SL/TP prices if pips provided
    if sl_pips is not None or tp_pips is not None:
        bid, ask = _latest_bid_ask(instrument)
        entry_ref = ask if side == "buy" else bid
        if sl_pips is not None and sl_price is None:
            sl_price = entry_ref - sl_pips * PIP if side == "buy" else entry_ref + sl_pips * PIP
        if tp_pips is not None and tp_price is None:
            tp_price = entry_ref + tp_pips * PIP if side == "buy" else entry_ref - tp_pips * PIP

    # Build order payload
    signed_units = units if side == "buy" else -abs(units)
    order = {
        "order": {
            "instrument": instrument,
            "units": str(signed_units),
            "type": "MARKET",
            "timeInForce": "FOK",       # fill-or-kill for market orders
            "positionFill": "DEFAULT",
            "clientExtensions": {"tag": client_tag}
        }
    }

    # Attach SL/TP if provided
    if sl_price is not None:
        order["order"]["stopLossOnFill"] = {"price": _round_price(sl_price)}
    if tp_price is not None:
        order["order"]["takeProfitOnFill"] = {"price": _round_price(tp_price)}

    # Send
    r = orders.OrderCreate(accountID=ACCOUNT_ID, data=order)
    try:
        client.request(r)
        print("Order submitted.")
        print(json.dumps(r.response, indent=2))
    except oandapyV20.exceptions.V20Error as e:
        print("OANDA V20 error:", e)
        if hasattr(r, "response") and r.response:
            print(json.dumps(r.response, indent=2))
            
            
def trade_CCY(volume, CCY, tag):
    rolling_sma = get_candles_and_rolling_sma(CCY)
    sma = get_candles_and_sma(CCY)

    if sma > rolling_sma[-1]:
        place_market_order(CCY, side="buy", units=volume, sl_pips=20, tp_pips=40, client_tag = tag)


    if sma < rolling_sma[-1]:
        place_market_order(CCY, side="sell", units=volume, sl_pips=20, tp_pips=40, client_tag = tag)


# ── EXAMPLES ───────────────────────────────────────────────────────────────────
def main():

    trade_CCY(1000, "EUR_USD", "EURUSD_MKT")
    trade_CCY(1000, "AUD_USD", "AUDUSD_MKT")
    trade_CCY(1000, "EUR_CHF", "EURCHF_MKT")
    trade_CCY(1000, "EUR_GBP", "EURGBP_MKT")
    trade_CCY(1000, "GBP_USD", "GBPUSD_MKT")
    trade_CCY(1000, "USD_CAD", "USDCAD_MKT")
    trade_CCY(1000, "USD_CHF", "USDCHF_MKT")
    trade_CCY(1000, "NZD_USD", "NZDUSD_MKT")
    
    


main()
