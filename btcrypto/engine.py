import copy


class Account(object):
    def __init__(self,
                 data=None,
                 capital=None,
                 risk=None,
                 percentage_of_capital_invested=None,
                 commission=None,
                 base_asset=None,
                 quote_asset=None,
                 take_profit_at=None):
        self.data = data
        self.capital = capital

        assert self.quote_asset in capital or self.base_asset in capital

        self.open_positions = []
        self.closed_positions = []
        self.risk = risk
        self.capital_to_invest = percentage_of_capital_invested
        self.commission = commission
        self.base_asset = base_asset
        self.quote_asset = quote_asset
        self.take_profit_at = take_profit_at

    def close_open_position(self, current_candle):
        open_position_deep_copy = copy.deepcopy(self.open_positions)
        if self.open_positions:
            for i, pos in enumerate(self.open_positions):
                deep_copy_position = copy.deepcopy(pos)
                if pos['type'] == 'long':
                    if current_candle['high'] > pos['take_profit_price']:
                        deep_copy_position['status'] = 'closed'
                        deep_copy_position['return_cost'] = pos['amount_bought'] * pos['take_profit_price']
                        deep_copy_position['pnl'] = (deep_copy_position['return_cost'] * (
                                    1 - (self.commission / 100))) - deep_copy_position['capital']
                        deep_copy_position['executed_time'] = pos['datetime']

                        self.closed_positions.append(deep_copy_position)
                        open_position_deep_copy.pop(i)
                        self.capital[self.quote_asset] += deep_copy_position['return_cost']
                    elif current_candle['low'] < pos['stop_loss_price']:
                        deep_copy_position['status'] = 'closed'
                        deep_copy_position['return_cost'] = pos['amount_bought'] * pos['stop_loss_price']
                        deep_copy_position['pnl'] = (deep_copy_position['return_cost'] * (
                                    1 - (self.commission / 100))) - deep_copy_position['capital']
                        deep_copy_position['executed_time'] = pos['datetime']

                        self.closed_positions.append(deep_copy_position)
                        open_position_deep_copy.pop(i)
                        self.capital[self.quote_asset] += deep_copy_position['return_cost']
                elif pos['type'] == 'short':
                    if current_candle['high'] > pos['stop_loss_price']:
                        deep_copy_position['status'] = 'closed'
                        deep_copy_position['return_cost'] = pos['amount_bought'] / pos['stop_loss_price']
                        deep_copy_position['pnl'] = (deep_copy_position['return_cost'] * (
                                    1 - (self.commission / 100))) - deep_copy_position['capital']
                        deep_copy_position['executed_time'] = pos['datetime']

                        self.closed_positions.append(deep_copy_position)
                        open_position_deep_copy.pop(i)
                        self.capital[self.base_asset] += deep_copy_position['return_cost']
                    elif current_candle['low'] < pos['take_profit_price']:
                        deep_copy_position['status'] = 'closed'
                        deep_copy_position['return_cost'] = pos['amount_bought'] / pos['take_profit_price']
                        deep_copy_position['pnl'] = (deep_copy_position['return_cost'] * (
                                    1 - (self.commission / 100))) - deep_copy_position['capital']
                        deep_copy_position['executed_time'] = pos['datetime']

                        self.closed_positions.append(deep_copy_position)
                        open_position_deep_copy.pop(i)
                        self.capital[self.base_asset] += deep_copy_position['return_cost']

        self.open_positions = open_position_deep_copy

    def logic(self):
        try:
            for candle in self.data.iterrows():
                self.close_open_position(candle)
                if candle['buy'] and self.capital > 0:
                    capital_to_risk = self.capital[self.quote_asset] * self.capital_to_invest / 100
                    position_taken_in = {'type': 'buy',
                                         'position': 'long',
                                         'status': 'open',
                                         'capital': capital_to_risk,
                                         'amount_bought': capital_to_risk / candle['close'],
                                         'entry_price': candle['close'],
                                         'take_profit_price': candle['close'] * (1 + (self.take_profit_at / 100)),
                                         'stop_loss_price': candle['close'] * (
                                                     1 - (self.take_profit_at / self.risk / 100))}
                    self.capital[self.quote_asset] -= capital_to_risk
                    self.open_positions.append(position_taken_in)
                elif candle['sell'] and self.capital > 0:
                    capital_to_risk = self.capital[self.base_asset] * self.capital_to_invest / 100
                    position_taken_in = {'type': 'sell',
                                         'position': 'short',
                                         'status': 'open',
                                         'capital': capital_to_risk,
                                         'amount_bought': capital_to_risk * candle['close'],
                                         'entry_price': candle['close'],
                                         'take_profit_price': candle['close'] * (1 - (self.take_profit_at / 100)),
                                         'stop_loss_price': candle['close'] * (
                                                     1 + (self.take_profit_at / self.risk / 100))}
                    self.capital[self.base_asset] -= capital_to_risk
                    self.open_positions.append(position_taken_in)
        except ValueError:
            pass
