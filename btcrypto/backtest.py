from finta import TA

from btcrypto.data import get_data
from btcrypto.utils import resample
from btcrypto.engine import Account


class BackTest(Account):
    def __init__(self,
                 data=None,
                 capital=None,
                 risk=None,
                 percentage_of_capital_invested=None,
                 commission=None,
                 base_asset=None,
                 quote_asset=None,
                 take_profit_at=None,
                 base_asset_minimum=10e-4,
                 quote_asset_minimum=10):
        super(BackTest, self).__init__(Account)
        self.data = data
        self.capital = capital
        self.open_positions = []
        self.closed_positions = []
        self.risk = risk
        self.capital_to_invest = percentage_of_capital_invested
        self.commission = commission
        self.base_asset = base_asset
        self.quote_asset = quote_asset
        self.take_profit_at = take_profit_at
        self.base_asset_minimum = base_asset_minimum
        self.quote_asset_minimum = quote_asset_minimum

    def do_backtest(self):
        try:
            for x, candle in enumerate(self.data.to_dict('records')):
                self.close_open_position(candle)
                if x != len(self.data) - 1:
                    if candle['decision'] == 'buy' and self.capital[self.quote_asset] > self.quote_asset_minimum:
                        capital_to_risk = self.capital[self.quote_asset] * self.capital_to_invest / 100
                        position_taken_in = {'type': 'buy',
                                             'position': 'long',
                                             'status': 'open',
                                             'capital': capital_to_risk,
                                             'amount_bought': capital_to_risk * (1 - (self.commission/100)) / candle['close'],
                                             'entry_price': candle['close'],
                                             'take_profit_price': candle['close'] * (1 + (self.take_profit_at / 100)),
                                             'stop_loss_price': candle['close'] * (
                                                     1 - (self.take_profit_at / self.risk / 100))}
                        self.capital[self.quote_asset] -= capital_to_risk
                        self.open_positions.append(position_taken_in)
                    elif candle['decision'] == 'sell' and self.capital[self.base_asset] > self.base_asset_minimum:
                        capital_to_risk = self.capital[self.base_asset] * self.capital_to_invest / 100
                        position_taken_in = {'type': 'sell',
                                             'position': 'short',
                                             'status': 'open',
                                             'capital': capital_to_risk,
                                             'amount_bought': capital_to_risk * (1 - (self.commission/100)) * candle['close'],
                                             'entry_price': candle['close'],
                                             'take_profit_price': candle['close'] * (1 - (self.take_profit_at / 100)),
                                             'stop_loss_price': candle['close'] * (
                                                     1 + (self.take_profit_at / self.risk / 100))}
                        self.capital[self.base_asset] -= capital_to_risk
                        self.open_positions.append(position_taken_in)
                else:
                    self.close_open_position(candle, force_close=True)
        except ValueError:
            pass


if __name__ == '__main__':
    df = get_data("BTCUSDT", "1d")
    df_1 = resample(df, 'D', time_column='close_datetime')
    df_1['sma_9'] = TA.SMA(df_1, period=9)
    df_1['sma_21'] = TA.SMA(df_1, period=21)
    df_1 = df_1.dropna()
    df_1['decision'] = df_1.apply(lambda a: ('buy' if a['sma_9'] > a['sma_21'] else 'sell') if a['sma_9'] and a['sma_21'] else None, axis=1)
    df_1['decision'] = df_1['decision'].shift(periods=1)
    df_1 = df_1.reset_index()

    inst = BackTest(data=df_1,
                    capital={'BTC': 0, 'USDT': 1000},
                    risk=2,
                    percentage_of_capital_invested=100,
                    commission=0.01,
                    base_asset='BTC',
                    quote_asset='USDT',
                    take_profit_at=3)
    inst.do_backtest()
