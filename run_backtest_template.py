# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 09:45:00 2020

@author: Nick Elmer

Do not use this file at the moment. I am still in the process of completing and
testing it.
"""
from datetime import datetime, date
import pandas as pd
from Backtest import get_norgatedata, initialise, update, plot_results, get_valid_dates
from _TechnicalIndicators import *
import data
from tqdm import tqdm

class Run_Backtest:

    def __init__(self, data, indicators, trade_open, trade_close):
        self.indicators = indicators
        self.trade_open = trade_open
        self.trade_close = trade_close



def run_single_backtest(stock_data, # Either a universe or a list of stock
                        before_backtest_start, # A function to be run before the backtest begins
                        trade_open, # A function containing rules to trade at the open
                        trade_close, # A function containing rules to trade at close
                        data_fields=['Open','High','Low','Close'],
                        data_adjustment='TotalReturn',
                        parameters = {}, # I don't think this is needed for a single backtest
                        indicators={}, # A dictionary containg a string of the function name from _Technical indicators as the key, and the inputs as the value in a list
                        rebalance='daily', # To be selected from drop-down menu
                        max_lookback=200,
                        starting_cash=100000,
                        data_source='Norgate', # To be selected from drop-down
                        start_date=date(2000,1,1),
                        end_date=datetime.now().date()):

    data.starting_amount = starting_cash

    if type(stock_data) == list:
        data_start = start_date - pd.tseries.offsets.BDay(max_lookback+10) # +10 to be on the safe side.
        get_norgatedata(stock_data,
                        fields=data_fields,
                        start_date=data_start,
                        end_date=end_date,
                        start_when_all_are_in=False,
                        adjustment=data_adjustment)
    else:
        raise ValueError('Currently not developed enough for more complex universes')

    new_date_list = get_valid_dates(max_lookback=max_lookback,
                                    rebalance=rebalance,
                                    start_trading=start_date,
                                    end_trading=end_date)
    indicator_variables = []
    for indicator, params in indicators.items(): # Here I create the indicator variable names.
        var_name = indicator.lower()
        for param in params:
            var_name += '_' + str(param)
        exec('{} = {}({})'.format(var_name, indicator, params))

    initialise()
    before_trading_start(data)

    pbar = tqdm(total=len(data.all_dates), position=0, desc='Running backtest')
    for d in data.all_dates:
        data.current_date = d

        if d in new_date_list:
            data.current_price = data.daily_opens.loc[d]
            trade_open(data)
            data.current_price = data.daily_closes.loc[d]
            trade_close(data)

        update()
        pbar.update(1)
