import time
import pyupbit
import datetime

access = ""
secret = ""

k = 0.6
tickers = ["KRW-BTC", "KRW-ETH", "KRW-BCH", "KRW-LTC", "KRW-NEO", "KRW-BTG",
           "KRW-ETC", "KRW-STRK", "KRW-LINK", "KRW-DOT", "KRW-WAVES", "KRW-FLOW"
           "KRW-QTUM", "KRW-GAS", "KRW-EOS", "KRW-OMG", "KRW-TON", "KRW-CBK",
           "KRW-DAWN", "KRW-ONT", "KRW-ADA", "KRW-XRP", "KRW-XLM", "KRW-HIVE", "KRW-DOGE"]
bought_ticker = {}


def get_target_price(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)

    target_price = df.iloc[0]['close'] + \
        (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price


def get_start_time(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="minute240", count=1)
    start_time = df.index[0]
    return start_time


def get_price_ma(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="minute240", count=6)
    ma = df['close'].rolling(5).mean().shift(1)
    return ma[-1]


def get_balance(ticker):
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0


def get_avg_buy_price(ticker):
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['avg_buy_price'] is not None:
                return float(b['avg_buy_price'])
            else:
                return 0
    return 0


def get_current_price(ticker):
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]


# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()

        if not bought_ticker:
            for ticker in tickers:
                start_time = get_start_time(ticker)
                end_time = start_time + datetime.timedelta(hours=4)
                if start_time < now < end_time - datetime.timedelta(seconds=30):
                    target_price = get_target_price(ticker)
                    price_ma = get_price_ma(ticker)
                    current_price = get_current_price(ticker)

                    if target_price < current_price and price_ma < current_price:
                        krw = get_balance("KRW")
                        if krw > 5000:
                            upbit.buy_market_order(ticker, krw*0.9995)
                            bought_ticker[ticker] = True
                time.sleep(1)
        else:
            ticker = list(bought_ticker.keys())[0]
            start_time = get_start_time(ticker)
            end_time = start_time + datetime.timedelta(hours=4)
            ticker_balance = get_balance(ticker[4:])
            avr_buy_price = get_avg_buy_price(ticker[4:])
            current_price = get_current_price(ticker)

            if now >= end_time:
                if ticker_balance * avr_buy_price > 5000:
                    upbit.sell_market_order(ticker, ticker_balance*0.9995)
                    bought_ticker.pop(ticker, None)
            if avr_buy_price * 1.07 < current_price or avr_buy_price * 0.97 > current_price:
                if ticker_balance * avr_buy_price > 5000:
                    upbit.sell_market_order(ticker, ticker_balance*0.9995)
                    bought_ticker.pop(ticker, None)

        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
