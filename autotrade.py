import time
import pyupbit
import datetime

access = ""
secret = ""

k = 0.4
h = 1.2
tickers = pyupbit.get_tickers(fiat="KRW")
bought_ticker = {}


def get_target_price(ticker):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute240", count=2)
    target_price = df.iloc[0]['close'] + \
        (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price


def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute240", count=1)
    start_time = df.index[0]
    return start_time


def get_volume_ma(ticker):
    """5시간 거개량 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute60", count=6)
    volume = df['volume'].rolling(5).mean().shift(1)
    return volume[-1]


def get_price_ma(ticker):
    """10시간 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute60", count=11)
    ma = df['close'].rolling(10).mean().shift(1)
    return ma[-1]


def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0


def get_avg_buy_price(ticker):
    """ 매수 평균가 조회 """
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['avg_buy_price'] is not None:
                return float(b['avg_buy_price'])
            else:
                return 0


def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]


def get_current_volume(ticker):
    """현재 거래량 조회"""
    one_hour_df = pyupbit.get_ohlcv(ticker, interval="minute60", count=1)
    return one_hour_df['volume'][0]


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
                    volume_ma = get_volume_ma(ticker)
                    current_volume = get_current_volume(ticker)

                    if target_price < current_price and price_ma < current_price and volume_ma * h < current_volume:
                        krw = get_balance("KRW")
                        if krw > 5000:
                            upbit.buy_market_order(ticker, krw*0.9995)
                            bought_ticker[ticker] = True
                time.sleep(1)
        else:
            start_time = get_start_time(ticker)
            end_time = start_time + datetime.timedelta(hours=4)
            ticker_balance = get_balance(ticker[4:])
            avr_buy_price = get_avg_buy_price(ticker)

            if now >= end_time - datetime.timedelta(seconds=30):
                if ticker_balance * avr_buy_price > 5000:
                    upbit.sell_market_order(ticker, ticker_balance*0.9995)
                    bought_ticker.pop(ticker, None)
            if avr_buy_price * 1.04 < current_price or avr_buy_price * 0.98 > current_price:
                if ticker_balance * avr_buy_price > 5000:
                    upbit.sell_market_order(ticker, ticker_balance*0.9995)
                    bought_ticker.pop(ticker, None)

        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
