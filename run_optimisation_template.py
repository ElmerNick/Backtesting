# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 14:45:31 2020

@author: Nick Elmer
"""
from datetime import datetime, date
import pandas as pd
from Backtest import get_norgatedata, initialise, update, plot_results, get_valid_dates, Orders
import Optimise
import data
import user
from tqdm import tqdm


def run_optimisation(stock_data,  # Either a universe or a list of stock
                     before_backtest_start,  # A function to be run before the backtest begins
                     trade_open,  # A function containing rules to trade at the open
                     trade_close,  # A function containing rules to trade at close
                     trade_every_day_open,
                     trade_every_day_close,
                     results_save_location,
                     opt_params={},
                     data_fields=['Open', 'High', 'Low', 'Close'],
                     data_adjustment='TotalReturn',
                     rebalance='daily',  # To be selected from drop-down menu
                     max_lookback=200,
                     starting_cash=100000,
                     data_source='Norgate',  # To be selected from drop-down
                     start_date=date(2000, 1, 1),
                     end_date=datetime.now().date()):
    data.starting_amount = starting_cash
    data.optimising = True

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

    Optimise.create_variable_combinations_dict(opt_params)
    number_of_rows = len(data.combination_df)
    print('Total number of tests:', number_of_rows)

    for i in range(number_of_rows):
        for j in range(len(data.combination_df.columns)):
            variable = data.combination_df.columns[j]
            value = data.combination_df.iat[i, j]
            exec('user.{} = {}'.format(variable, value))

        before_backtest_start(user, data)
        initialise()
        pbar = tqdm(total=len(data.all_dates), position=0, leave=True, desc='Test {}'.format(str(i+1)))
        for d in data.all_dates:
            data.current_date = d

            data.current_price = data.daily_opens.loc[d]
            trade_every_day_open(user, data)

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

        Optimise.record_backtest(combination_row=i)
        if results_save_location != '':
            data.optimisation_report.to_csv('{}\\temp.csv'.format(results_save_location),
                                            index=True, index_label='Test_Number')
        pbar.close()
    if results_save_location != '':
        data.optimisation_report.to_csv(
                '{}\\Results_{}.csv'.format(results_save_location, datetime.now().strftime('%d%m%y %H%M')),
                index=True, index_label='Test_Number')

    if number_of_rows == 1:
        plot_results()



def _download_norgate_data(stock_data,
                           start_date,
                           end_date,
                           max_lookback,
                           data_fields,
                           data_adjustment):
    import norgatedata
    data_start = start_date - pd.tseries.offsets.BDay(max_lookback + 10)

    symbols = set()
    for s in stock_data:
        if type(s) == tuple:
            for stock in s:
                symbols.add(norgatedata.assetid(stock))
        elif s[:6] == 'Liquid':
            if s == 'Liquid_500':
                daily_universes = pd.read_csv(
                    r'C:\Users\User\Documents\Backtesting_Creation\Dev\Universes\US_Liquid_500_most_recent.csv',
                    index_col=0, parse_dates=True)
            elif s == 'Liquid_1500':
                daily_universes = pd.read_csv(
                    r'C:\Users\User\Documents\Backtesting_Creation\Dev\Universes\US_Liquid_1500_most_recent.csv',
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
