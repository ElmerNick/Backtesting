# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 11:57:21 2020

@author: Nick Elmer
"""

import pandas as pd
import itertools
import data
from plotly.offline import plot
import plotly.graph_objects as go


def create_variable_combinations(list_of_series):
    '''
    Creates a dataframe with column headers that are the names of the variables
    to be optimised on. The rows contain every possible combination of the
    parameters.

    Parameters
    ----------
    list_of_series : list
        A list containing series that have the name of the variable as the
        series name, and the values that are the differnt values to be
        optimised for.

    Returns
    -------
    None. Creates a combination dataframe in data.combination_df. Creates an
    empty optimisation report in data.optimisation_report. Creates an empty
    list to store lists of wealth tracks in data.optimisation_wealth_tracks.

    '''
    variable_names = []
    list_of_lists = []
    for series in list_of_series:
        variable_names.append(series.name)
        list_of_lists.append(series.tolist())
    
    combinations = itertools.product(*list_of_lists)
    combo_list = []
    for combo in combinations:
        combo_list.append(combo)
    
    combo_df = pd.DataFrame(index=range(len(combo_list)), columns=variable_names)
    for i in range(len(combo_list)):
        combo = combo_list[i]
        combo_df.iloc[i] = combo
    
    data.combination_df = combo_df
    
    data.optimisation_report = pd.DataFrame(index=range(len(combo_df)),
                                            columns=combo_df.columns)
    data.optimisation_wealth_tracks = []
    data.length_of_backtest = 0
        
def record_backtest(combination_row):
    '''
    Called at the end of every backtest record the results in
    data.optimisation_report.

    Parameters
    ----------
    combination_row : int
        The test number of the optimisation.

    Returns
    -------
    None. Stores the results of the backtest in data.optimisation_report.

    '''
    total_profit = data.wealth_track[-1] - data.starting_amount
    wealth_track_df = pd.Series(data=data.wealth_track, index=data.date_track, name=combination_row)
    data.optimisation_wealth_tracks.append(wealth_track_df)
    if data.length_of_backtest == 0:
        data.length_of_backtest = len(data.wealth_track) / 252
    profit_as_percent = 100*(total_profit / data.starting_amount)
    realised_rate = profit_as_percent / data.length_of_backtest
    
    
    data.optimisation_report.loc[combination_row] = data.combination_df.iloc[combination_row]
    data.optimisation_report.at[combination_row, 'total_profit'] = total_profit
    data.optimisation_report.at[combination_row, 'realised_rate'] = realised_rate

def plot_tests(test_numbers, title=None):
    fig = go.Figure()
    for n in test_numbers:
        profit_series = data.optimisation_wealth_tracks[n] - 100000
        final_equity = profit_series.iloc[-1]
        fig.add_trace(go.Scatter(x=profit_series.index, y=profit_series, name=str(n) + ' ' + str(final_equity)))
    
    fig.update_layout(template='plotly_dark', title=title)
    plot(fig, auto_open=True)
    
def average_per_parameter(results):
    averages_df = pd.DataFrame(columns=['average'])
    for param in data.combination_df.columns:
        variations = results[param].value_counts().index
        for val in variations:
            average = results[results[param]==val]['total_profit'].mean()
            index_label = str(param) + ' = ' + str(val)
            averages_df.at[index_label, 'average'] = average
    return averages_df
    

    

















