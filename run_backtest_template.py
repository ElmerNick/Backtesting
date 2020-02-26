# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 09:45:00 2020

@author: Nick Elmer

Do not use this file at the moment. I am still in the process of completing and
testing it.
"""
from datetime import datetime, date
import pandas as pd
from Backtest import get_norgatedata, initialise, update, plot_results, get_valid_dates, Orders
import data
import user
from tqdm import tqdm


def run_single_backtest(stock_data,  # Either a universe or a list of stock
                        before_backtest_start,  # A function to be run before the backtest begins
                        trade_open,  # A function containing rules to trade at the open
                        trade_close,  # A function containing rules to trade at close
                        trade_every_day_close,
                        data_fields=['Open', 'High', 'Low', 'Close'],
                        data_adjustment='TotalReturn',
                        rebalance='daily',  # To be selected from drop-down menu
                        max_lookback=200,
                        starting_cash=100000,
                        data_source='Norgate',  # To be selected from drop-down
                        start_date=date(2000, 1, 1),
                        end_date=datetime.now().date()):
    data.starting_amount = starting_cash
    data.optimising = False

    # if type(stock_data) == list:
    #     data_start = start_date - pd.tseries.offsets.BDay(max_lookback+10) # +10 to be on the safe side.
    #     get_norgatedata(stock_data,
    #                     fields=data_fields,
    #                     start_date=data_start,
    #                     end_date=end_date,
    #                     start_when_all_are_in=False,
    #                     adjustment=data_adjustment)
    # elif stock_data == 'Liquid_500':
    #     daily_universes = pd.read_csv(r'C:\Users\User\Documents\Backtesting_Creation\Dev\Universes\US_Liquid_500_most_recent.csv', index_col=0, parse_dates=True)
    #     daily_universes = daily_universes.dropna(how='all')
    #     daily_universes = daily_universes.astype(int)
    #     unique_universes = daily_universes.drop_duplicates()
    #     symbols = set()
    #     for col in unique_universes.columns:
    #         symbols = symbols.union(unique_universes[col].unique())
    #     symbols = list(symbols)

    if data_source == 'Norgate':
        _download_norgate_data(stock_data,
                               start_date,
                               end_date,
                               max_lookback,
                               data_fields,
                               data_adjustment)

    new_date_list = get_valid_dates(max_lookback=max_lookback,
                                    rebalance=rebalance,
                                    start_trading=start_date,
                                    end_trading=end_date)
    # indicator_variables = []
    # for indicator, params in indicators.items(): # Here I create the indicator variable names.
    #     var_name = indicator.lower()
    #     for param in params:
    #         var_name += '_' + str(param)
    #     exec('{} = {}({})'.format(var_name, indicator, params))

    initialise()
    before_backtest_start(user, data)

    pbar = tqdm(total=len(data.all_dates), position=0, desc='Running backtest')
    for d in data.all_dates:
        data.current_date = d

        if d in new_date_list:
            data.current_price = data.daily_opens.loc[d]
            trade_open(user, data)
            data.current_price = data.daily_closes.loc[d]
            trade_close(user, data)

        data.current_price = data.daily_closes.loc[d]
        trade_every_day_close(user, data)

        update()
        pbar.update(1)
    for x in list(data.current_positions):
        Orders(x, close_reason='End of backtest').order_target_amount(0)
    pbar.close()

    plot_results()


def _download_norgate_data(stock_data,
                           start_date,
                           end_date,
                           max_lookback,
                           data_fields,
                           data_adjustment):
    data_start = start_date - pd.tseries.offsets.BDay(max_lookback + 10)

    symbols = set()
    for s in stock_data:
        if type(s) == tuple:
            for stock in s:
                symbols.add(norgatedata.assetid(stock))
        elif s == 'Liquid_500':
            daily_universes = pd.read_csv(
                r'C:\Users\User\Documents\Backtesting_Creation\Dev\Universes\US_Liquid_500_most_recent.csv',
                index_col=0, parse_dates=True)
            daily_universes = daily_universes.dropna(how='all')
            daily_universes = daily_universes.loc[start_date:end_date]
            daily_universes.dropna(axis=1, how='all', inplace=True)
            daily_universes = daily_universes.astype(int)
            unique_universes = daily_universes.drop_duplicates()
            syms = set()
            for col in unique_universes.columns:
                syms = syms.union(unique_universes[col].unique())
            data.daily_universes = daily_universes
            symbols = symbols.union(syms)
    get_norgatedata(symbols,
                    fields=data_fields,
                    start_date=data_start,
                    end_date=end_date,
                    start_when_all_are_in=False,
                    adjustment=data_adjustment)
