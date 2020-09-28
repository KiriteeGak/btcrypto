from datetime import datetime
import pandas as pd
import requests


def get_data(coin_pairing, time_aggregated=None):
    """
    Gets OHLCV data from binance exchange for a coin pairing for the given time aggregate
    :param coin_pairing: Pass the pairing for which you want to receive that candle stick data.
    To get all pairings available ask `get_pairings()`
    :param time_aggregated: Time on which a single candle should be aggregated; defaults to 5m
    :return: A dataframe of ohlcv values
    """
    binance_basic_kline_api = "https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=1000"

    interval = '5m' if not time_aggregated else time_aggregated

    assert coin_pairing in get_pairings(), "no coin_pairing {} found in binance listed pairings".format(coin_pairing)

    api_ = binance_basic_kline_api.format(symbol=coin_pairing, interval=interval)
    data_received = requests.get(api_).json()
    if data_received:
        data = [dict(zip(['open_time', 'open', 'high', 'low', 'close',
                          'volume', 'close_time', 'quote_asset_volume',
                          'number_of_trades', 'taker_buy_base_asset_volume',
                          'taker_buy_quote_asset_volume', 'ignore', 'coin_pairing',
                          'close_datetime', 'open_datetime', 'interval'],
                         c_bars +
                         [coin_pairing,
                          datetime.fromtimestamp(float(c_bars[6]) / 1000),
                          datetime.fromtimestamp(float(c_bars[0]) / 1000),
                          interval]))
                for c_bars in data_received]
        return pd.DataFrame(data).astype({'open': float, 'close': float, 'high': float, 'low': float, 'volume': float})
    return None


def get_pairings():
    """
    Gets all pairings available on binance exchange at the current time
    :return:
    """
    resp = requests.get("https://www.binance.com/api/v1/exchangeInfo").json()
    return [x['symbol'] for x in resp['symbols']]


if __name__ == '__main__':
    from btcrypto.utils import resample
    df = get_data("BTCUSDT", "1d")
    df_1 = resample(df, 'W', time_column='close_datetime')
    df.to_csv("df.csv")
    df_1.to_csv("df1.csv")
