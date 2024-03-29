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
import numpy as np


def create_variable_combinations(list_of_series):
    """
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

    """
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


def create_variable_combinations_dict(param_dict, optimise_type):
    variable_names = []
    list_of_tuples = []
    for variable, params in param_dict.items():
        variable_names.append(variable)
        list_of_tuples.append(params)

    if optimise_type == 'combination' or param_dict == {}:
        combinations = itertools.product(*list_of_tuples)
        combo_list = []
        for combo in combinations:
            combo_list.append(combo)
    elif optimise_type == 'fixed':
        combo_list = []
        for i in range(len(list_of_tuples[0])):
            combo_list.append([tup[i] for tup in list_of_tuples])

    combo_df = pd.DataFrame(data=combo_list, columns=variable_names, dtype=object)
    # for i in range(len(combo_list)):
    #     combo = combo_list[i]
    #     combo_df.iloc[i] = combo

    data.combination_df = combo_df

    data.optimisation_report = pd.DataFrame(index=range(len(combo_df)),
                                            columns=combo_df.columns)
    data.optimisation_wealth_tracks = []
    data.length_of_backtest = 0


def record_backtest(combination_row):
    """
    Called at the end of every backtest record the results in
    data.optimisation_report.

    Parameters
    ----------
    combination_row : int
        The test number of the optimisation.

    Returns
    -------
    None. Stores the results of the backtest in data.optimisation_report.

    """
    total_profit = data.wealth_track[-1] - data.starting_amount
    wealth_track_df = pd.Series(data=data.wealth_track, index=data.date_track, name=combination_row)
    data.optimisation_wealth_tracks.append(wealth_track_df)
    if data.length_of_backtest == 0:
        data.length_of_backtest = len(data.wealth_track) / 252
    profit_as_percent = 100 * (total_profit / data.starting_amount)
    realised_rate = profit_as_percent / data.length_of_backtest
    equity = wealth_track_df - data.starting_amount
    drawdown = equity - equity.cummax()
    max_dd = drawdown.min()
    max_dd_percent = 100 * max_dd / data.starting_amount
    max_dd_date = drawdown.idxmin()
    max_dd_start = drawdown.where(drawdown==0, np.nan).loc[:max_dd_date].last_valid_index()
    max_dd_end = drawdown.where(drawdown==0, np.nan).loc[max_dd_date:].first_valid_index()
    max_dd_length = len(drawdown[max_dd_start:max_dd_end])

    data.optimisation_report.loc[combination_row] = data.combination_df.iloc[combination_row]
    data.optimisation_report.at[combination_row, 'total_profit'] = total_profit
    data.optimisation_report.at[combination_row, 'realised_rate'] = realised_rate
    data.optimisation_report.at[combination_row, 'number_of_trades'] = data.number_of_trades
    try:
        data.optimisation_report.at[combination_row, 'percent profitable trades'] = 100 * \
                                                                    (data.number_winning_trades / data.number_of_trades)
        data.optimisation_report.at[combination_row, 'average_trade_net_profit'] = total_profit / data.number_of_trades
        data.optimisation_report.at[combination_row, 'average_trade_%_profit'] = data.profit_percent_array.mean()
    except ZeroDivisionError:
        data.optimisation_report.at[combination_row, 'percent profitable trades'] = 0
        data.optimisation_report.at[combination_row, 'average_trade_net_profit'] = 0
        data.optimisation_report.at[combination_row, 'average_trade_%_profit'] = 0
    data.optimisation_report.at[combination_row, 'max_drawdown'] = max_dd
    data.optimisation_report.at[combination_row, 'max_drawdown%'] = max_dd_percent
    data.optimisation_report.at[combination_row, 'length_of_max_drawdown'] = max_dd_length

    yearly_profits = wealth_track_df.resample('Y').last().diff()
    yearly_profits.index = yearly_profits.index.year
    yearly_profits *= 100 / data.starting_amount
    for year in yearly_profits.index:
        data.optimisation_report.at[combination_row, year] = yearly_profits[year]
    stddev_yearly_returns = yearly_profits.std()
    data.optimisation_report.at[combination_row, 'Standard Dev of Yearly Returns'] = stddev_yearly_returns
    data.optimisation_report.at[combination_row, r'Rate / StdDev'] = realised_rate / stddev_yearly_returns


def plot_tests(test_numbers, title=None):
    """
    Provide some test numbers from the optimisation just run to plot.

    After running an optimisation, whilst you still have the
    data.optimisation_wealth_tracks variable accessible by your editor. This
    function will produce a plotly line graph of the tests that you provide as
    a list.

    Parameters
    ----------
    test_numbers : list
        A list of integers referring to test numbers of an optimsation report.
    title : str, default None
        The title you would like to appear at the top of the plot.

    Returns
    -------
    None
        Automatically opens a .html plot in your default browser.

    Examples
    -------
    Examples should be written in doctest format, and
    should illustrate how to use the function/class.
    >>>

    """
    fig = go.Figure()

    max_profit = max(max(x) for x in data.optimisation_wealth_tracks) - data.starting_amount
    in_out_samples = pd.DataFrame(index=data.all_dates.union(data.oos_dates), columns=['IS', 'OOS'])
    in_out_samples['IS'].loc[data.is_dates] = max_profit * 1.05
    in_out_samples['OOS'].loc[data.oos_dates] = max_profit * 1.05
    in_out_samples.fillna(0, inplace=True)
    fig.add_trace(go.Scatter(x=in_out_samples.index, y=in_out_samples['IS'],
                             name='In Sample', marker_color='green', fill='tozeroy', line_shape='hv'))
    fig.add_trace(go.Scatter(x=in_out_samples.index, y=in_out_samples['OOS'],
                             name='Out of Sample', marker_color='red', fill='tozeroy', line_shape='hv'))

    for n in test_numbers:
        profit_series = data.optimisation_wealth_tracks[n] - 100000
        final_equity = profit_series.iloc[-1]
        fig.add_trace(go.Scatter(x=profit_series.index, y=profit_series, name=str(n) + ' ' + str(final_equity)))

    fig.update_layout(template='plotly_dark', title=title)
    plot(fig, auto_open=True)


def average_per_parameter(results):
    """
    Get the average profit over all optimsations for each parameter variation.

    For each parameter and each value it can take in an optimisation, this
    calculates the average total profit produced by it.

    Parameters
    ----------
    results : pandas-dataframe
        A dataframe of the results of the optimisation.

    Returns
    -------
    pandas-series
        Series with all the relevent information

    Examples
    -------
    Examples should be written in doctest format, and
    should illustrate how to use the function/class.
    >>>

    """
    averages_df = pd.DataFrame(columns=['average'])
    for param in data.combination_df.columns:
        variations = results[param].value_counts().index
        for val in variations:
            average = results[results[param] == val]['total_profit'].mean()
            index_label = str(param) + ' = ' + str(val)
            averages_df.at[index_label, 'average'] = average
    return averages_df
