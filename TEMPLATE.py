# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 15:10:19 2020

@author: Nick Elmer
"""

from Backtest import Orders, get_valid_dates, run
import pandas as pd
from datetime import date
from _TechnicalIndicators import RSI


def before_backtest_start(user, data):
    return


def trade_every_day_open(user, data):
    d = data.current_date
    index_today = data.daily_closes.index.get_loc(d)
    return


def trade_open(user, data):
    d = data.current_date
    index_today = data.daily_closes.index.get_loc(d)
    return


def trade_close(user, data):
    d = data.current_date
    index_today = data.daily_closes.index.get_loc(d)
    return


def trade_every_day_close(user, data):
    d = data.current_date
    index_today = data.daily_closes.index.get_loc(d)
    return


stock_data = {'Liquid_500', ('SPY',)}

save_location_of_report = r''
params_to_optimise = {}
data_fields_needed = ['Open', 'High', 'Low', 'Close']  # Want to make into check boxes
data_adjustment = 'TotalReturn'  # Will be a radio button
rebalance = 'daily'  # Will be either radio buttons or dropdown menu
max_lookback = 200  # Integer input
starting_cash = 100000  # 2 dp. float input
data_source = 'Norgate'  # Dropdown menu
start_date = date(2000, 1, 1)  # Date select
end_date = date(2020, 2, 13)  # Date select

run(stock_data=stock_data,
    before_backtest_start=before_backtest_start,
    trade_every_day_open=trade_every_day_open,
    trade_open=trade_open,
    trade_close=trade_close,
    trade_every_day_close=trade_every_day_close,
    opt_results_save_loc=save_location_of_report,
    opt_params=params_to_optimise,
    data_fields=data_fields_needed,
    data_adjustment=data_adjustment,
    rebalance=rebalance,
    max_lookback=max_lookback,
    starting_cash=starting_cash,
    data_source='Norgate',
    start_date=start_date,
    end_date=end_date)
