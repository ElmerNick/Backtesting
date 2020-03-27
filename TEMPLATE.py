# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 15:10:19 2020

@author: Nick Elmer
"""

from Backtest import Orders, get_valid_dates, run
import pandas as pd
from datetime import date
from _TechnicalIndicators import RSI


def before_everything_starts(user, data):
    '''
    If you want anything run before any backtests start, then place it here. Any variables which will remain constant
    throughtout an optimisation can be defined here. You can also initalise any custom metrics here and record them in
    the functions below.
    '''
    return


def before_backtest_start(user, data):
    '''
    In here, code up anything that you wish to happen before each backtest starts. A good habit to get in to is to
    calculate all indicators here and then use them in the backtest. Any variables you wish to be accessible in the
    other function you must input `user.` in front. For anything that will be optimised it MUST have `user.` as a
    prefix.
    '''
    return


'''
In each of the functions below, two useful variables have been provided. `d` is the timestamp for the current day of
the backtest. `index_today` is the row number relating to this date in `data.daily_closes`. You can use `index_today`
for creating history variables.
'''
def trade_every_day_open(user, data):
    '''
    This is run every day regardless of `rebalance` frequency. If you are on a day where `trade_open` will execute, this
    function will run first.
    '''
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
    '''
    Similar to `trade_every_day_open` but runs after `trade_close`.
    '''
    d = data.current_date
    index_today = data.daily_closes.index.get_loc(d)
    return


def after_backtest_finish(user, data):
    '''
    This is run after each backtest finishes. If you are doing a single backtest, can use it to plot results or save
    files. If optimising, be weary that this will run after each backtest in the optimisation.
    '''
    return


'''
Input any equities or universes you wish to be included in the backtest. If a universe is chosen, the data for that will
be stored in `data.daily_universes`.
'''
stock_data = {'Liquid_500', ('SPY',)}

save_location_of_report = r''  # If optimising this will be where the optimisation report is saved.
'''
For optimisations, populate `params_to_optimise`. Write the name of the variable to optimise as the key, and the value
of the dictionary to be a tuple of the optimised parameters. The program will run the optimisation on every possible
combination of the parameters.
'''
params_to_optimise = {}
data_fields_needed = ['Open', 'High', 'Low', 'Close']  # The fields needed. If `check_stop_loss` is used, need OHLC
data_adjustment = 'TotalReturn'  # The type of adjustment of the data
rebalance = 'daily'  # 'daily', 'weekly', 'month-end', 'month-start'
max_lookback = 200
starting_cash = 100000  # 2 dp. float
data_source = 'Norgate'  # Either 'Norgate' or 'local_csv'
start_date = date(2000, 1, 1)  # The date trading will start
end_date = date(2020, 2, 13)  # The date trading will end

Results = run(stock_data=stock_data,
              before_everything_starts=before_everything_starts,
              before_backtest_start=before_backtest_start,
              trade_every_day_open=trade_every_day_open,
              trade_open=trade_open,
              trade_close=trade_close,
              trade_every_day_close=trade_every_day_close,
              after_backtest_finish=after_backtest_finish,
              opt_results_save_loc=save_location_of_report,
              opt_params=params_to_optimise,
              data_fields=data_fields_needed,
              data_adjustment=data_adjustment,
              rebalance=rebalance,
              max_lookback=max_lookback,
              starting_cash=starting_cash,
              data_source='Norgate',
              start_date=start_date,
              end_date=end_date,
              auto_plot=True,
              plot_title='Backtest')
