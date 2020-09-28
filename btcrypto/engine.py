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
                 take_profit_at=None,
                 base_asset_minimum=10e-4,
                 quote_asset_minimum=10):
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

    def close_open_position(self, current_candle, force_close=False):
        open_position_deep_copy = copy.deepcopy(self.open_positions)
        if self.open_positions:
            if not force_close:
                for i, pos in enumerate(self.open_positions):
                    deep_copy_position = copy.deepcopy(pos)
                    if pos['position'] == 'long':
                        if current_candle['high'] > pos['take_profit_price']:
                            deep_copy_position['status'] = 'closed'
                            deep_copy_position['return_cost'] = pos['amount_bought'] * pos['take_profit_price']
                            deep_copy_position['pnl'] = (deep_copy_position['return_cost'] * (
                                        1 - (self.commission / 100))) - deep_copy_position['capital']
                            deep_copy_position['executed_time'] = current_candle['close_datetime']

                            self.closed_positions.append(deep_copy_position)
                            open_position_deep_copy.pop(i)
                            self.capital[self.quote_asset] += deep_copy_position['return_cost']
                        elif current_candle['low'] < pos['stop_loss_price']:
                            deep_copy_position['status'] = 'closed'
                            deep_copy_position['return_cost'] = pos['amount_bought'] * pos['stop_loss_price']
                            deep_copy_position['pnl'] = (deep_copy_position['return_cost'] * (
                                        1 - (self.commission / 100))) - deep_copy_position['capital']
                            deep_copy_position['executed_time'] = current_candle['close_datetime']

                            self.closed_positions.append(deep_copy_position)
                            open_position_deep_copy.pop(i)
                            self.capital[self.quote_asset] += deep_copy_position['return_cost']
                    elif pos['position'] == 'short':
                        if current_candle['low'] < pos['take_profit_price']:
                            deep_copy_position['status'] = 'closed'
                            deep_copy_position['return_cost'] = pos['amount_bought'] / pos['take_profit_price']
                            deep_copy_position['pnl'] = (deep_copy_position['return_cost'] * (
                                    1 - (self.commission / 100))) - deep_copy_position['capital']
                            deep_copy_position['executed_time'] = current_candle['close_datetime']

                            self.closed_positions.append(deep_copy_position)
                            open_position_deep_copy.pop(i)
                            self.capital[self.base_asset] += deep_copy_position['return_cost']
                        elif current_candle['high'] > pos['stop_loss_price']:
                            deep_copy_position['status'] = 'closed'
                            deep_copy_position['return_cost'] = pos['amount_bought'] / pos['stop_loss_price']
                            deep_copy_position['pnl'] = (deep_copy_position['return_cost'] * (
                                        1 - (self.commission / 100))) - deep_copy_position['capital']
                            deep_copy_position['executed_time'] = current_candle['close_datetime']

                            self.closed_positions.append(deep_copy_position)
                            open_position_deep_copy.pop(i)
                            self.capital[self.base_asset] += deep_copy_position['return_cost']
            else:
                for i, pos in enumerate(self.open_positions):
                    deep_copy_position = copy.deepcopy(pos)
                    if pos['position'] == 'long':
                        deep_copy_position['status'] = 'closed'
                        deep_copy_position['return_cost'] = pos['amount_bought'] * current_candle['close']
                        deep_copy_position['pnl'] = (deep_copy_position['return_cost'] * (
                                1 - (self.commission / 100))) - deep_copy_position['capital']
                        deep_copy_position['executed_time'] = current_candle['close_datetime']

                        self.closed_positions.append(deep_copy_position)
                        open_position_deep_copy.pop(i)
                        self.capital[self.quote_asset] += deep_copy_position['return_cost']
                    elif pos['position'] == 'short':
                        deep_copy_position['status'] = 'closed'
                        deep_copy_position['return_cost'] = pos['amount_bought'] / current_candle['close']
                        deep_copy_position['pnl'] = (deep_copy_position['return_cost'] * (
                                1 - (self.commission / 100))) - deep_copy_position['capital']
                        deep_copy_position['executed_time'] = current_candle['close_datetime']

                        self.closed_positions.append(deep_copy_position)
                        open_position_deep_copy.pop(i)
                        self.capital[self.base_asset] += deep_copy_position['return_cost']
        self.open_positions = open_position_deep_copy
