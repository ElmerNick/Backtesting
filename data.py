# -*- coding: utf-8 -*-
"""
Created on Fri Dec 20 11:39:51 2019

@author: Nick Elmer
"""
# import pandas as pd
# import os
# from datetime import date
# from plotly.offline import plot
# import plotly.graph_objects as go


# def get_results(benchmark=None, start_date=date(2000,1,3), end_date=date(2019,12,31), title=None):
#     wealth_list = [x - 100000 for x in wealth_track]
#     equity_df = pd.DataFrame(columns=['date', 'equity'])
#     equity_df['date'] = date_track
#     equity_df['equity'] = wealth_list
#     equity_df.set_index('date', inplace=True)
#     equity_df = equity_df.loc[start_date:end_date]
#     equity_df['equity'] = equity_df['equity'] - equity_df['equity'].iloc[0]
    
#     fig = go.Figure([go.Scatter(x=equity_df.index, y=equity_df['equity'], name='My Strategy')])
#     if benchmark != None:
#         comparison_DW = pd.read_csv(benchmark, index_col=0, parse_dates=True)
#         comparison_DW = benchmark.loc[start_date:end_date]
#         comparison_DW['OpenEquity'] = comparison_DW['OpenEquity'] - comparison_DW['OpenEquity'].iloc[0]
#         fig.add_trace(go.Scatter(x=comparison_DW.index, y=comparison_DW['OpenEquity'], name='TradeStation results'))
#     fig.update_layout(template='plotly_dark', title=title)
#     plot(fig, auto_open=True)
    
    
# def update():
#     total_wealth = cash
#     all_open_trade_rows = trade_df[trade_df['close_price'].isnull()]
#     current_position_value = 0
#     for index, row in all_open_trade_rows.iterrows():
#         current_value = row['amount'] * current_price[row['symbol']]
#         if row['long_or_short'] == 'long':
#             current_position_value += current_value
#         else:
#             current_position_value -= (2 * row['open_value']) - current_value
#     total_wealth += current_position_value
#     wealth_track.append(total_wealth)
#     date_track.append(current_date)
    

# source_data_path = r'C:\Users\User\Documents\Backtesting_Creation\data_in_use\\'

# '''
# Changing parse_dates to False for Quantopian
# '''

# #minute_data_dfs = {fname[:-4] : pd.read_csv(source_data_path+'Minute\\'+fname, index_col=0, parse_dates=True) for fname in os.listdir(source_data_path+'Minute')}
# daily_data_dfs = {fname[:-4] : pd.read_csv(source_data_path+'Daily\\'+fname, index_col=0, parse_dates=False) for fname in os.listdir(source_data_path+'Daily')}
# symbols = [s for s in daily_data_dfs.keys()]
# del source_data_path

# start_date = date(2000,1,3)
# end_date = date(2019,12,31)

# all_dates = pd.date_range(start=start_date, end=end_date)
# daily_closes = pd.DataFrame(index=all_dates)
# for symbol, df in daily_data_dfs.items():
#     '''
#     Adding in the format of dates
#     '''
#     df.index = pd.to_datetime(df.index, format='%d/%m/%Y')
# #    if df.index[0] == '11/04/2007':
# #        df.index = pd.to_datetime(df.index, format='%d/%m/%Y')
# #    else:
# #        df.index = pd.to_datetime(df.index, format='%Y-%m-%d')
#     daily_closes[symbol] = df['Close']

# ###############################################################################
# '''
# SPECIFIC FOR QUANTOPIAN DATA
# '''
# '''
# trade_prices = pd.DataFrame(index=all_dates)
# for symbol, df in daily_data_dfs.items():
#     trade_prices[symbol] = df['Trade_Price']
# trade_prices = trade_prices.dropna(axis=0, how='any')
# '''
# ###############################################################################

# del symbol, df
 
# # Removing all days where no trades take place for any ticker    
# daily_closes = daily_closes.dropna(axis=0, how='any')
# all_dates = daily_closes.index
# start_date = all_dates[0]

# columns = ['long_or_short', 'symbol', 'open_date',
#            'open_price', 'amount', 'open_value', 'close_date', 'close_price',
#            'close_value', 'profit']
# trade_df = pd.DataFrame(columns=columns)
# positions_tracker = pd.DataFrame(index=daily_closes.index, columns=daily_closes.columns)
# wealth_track = []
# date_track = []
# current_positions = []
# starting_amount = 100000
# cash = 100000
# wealth = 100000




