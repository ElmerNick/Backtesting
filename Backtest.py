# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 08:39:14 2020

@author: Nick Elmer
"""
import pandas as pd
import data
from datetime import date
from math import floor, ceil
import norgatedata
from plotly.offline import plot
import plotly.graph_objects as go
import pandas_market_calendars as mcal
from datetime import datetime, timedelta
from tqdm import tqdm
import os

class Orders:
    '''
    Places orders of specified types of a stock.

    Parameters
    ----------
    symbol : str, or int
        Either a symbol of a stock, eg. 'AAPL', or an asset id of that stock.
        This must match the column header of the prices dataframe.
    open_reason : str, default None
        Populates the trade list 'open_reason' column in the trade list.
    close_reason : str, default None
        Populates the trade list 'close_reason' column in the trade list.
    compound : bool, default False
        Will affect the order_percent function and the order_target_percent
        functions. These function will place an order at a value as a percentage
        of your wealth instead of the starting amount.
    able_to_exceed : bool, default True
        If an order placed is such that the investment exeeds the starting
        amount, then the order will be adjusted to enter in as many share as
        possible without exceeding.
    min_to_enter : int, default 10
        The minimum number of shares you can open in a trade. eg. If value is
        set to 10 and you attempt to order 3, the order will not be placed.

    Examples
    -------
    Examples should be written in doctest format, and
    should illustrate how to use the function/class.
    >>>

    '''

    def __init__(self, symbol, open_reason=None, close_reason=None,
                 compound=False, able_to_exceed=True, min_to_enter=10):
        '''
        Initialising the placement of an order.

        Currently, you must have a file called data.py in the directory for the
        variables to be stored in.

        Parameters
        ----------
        symbol : str
            The acronymn for a ticker symbol of a stock.
        open_reason : str
            A label to put on the trade df for the reason the trade opened.
        close_reason : str
            A label to put on the trade df for the reason the trade closed.
        compound : bool, optional
            True if you want to compund invest. The default is False.
        able_to_exceed : bool, optional
            If set to True, this does not prevent spending more than your
            starting amount (or current wealth if compound is True).
        '''
        self.symbol = symbol
        self.all_open_trade_rows = data.trade_df[(data.trade_df['symbol']==symbol) & (data.trade_df['close_price'].isnull())] # Extract open position for symbol
        self.current_number_of_shares = self.all_open_trade_rows['amount'].sum(axis=0)
        self.date = data.current_date
        self.limit_passed = False
        self.open_reason = open_reason
        self.close_reason = close_reason
        self.able_to_exceed = able_to_exceed
        self.price = data.current_price[symbol]
        self.min_to_enter = min_to_enter
        if compound == False:
            self.capital = data.starting_amount
        else:
            self.capital = data.wealth_track[-1]

    def order_amount(self, amount, limit_price=None):
        '''
        Places an order for a desired amount of shares. Would not recommend as
        it would be simpler to use order_target_amount. If a negative amount
        is entered, this will place a short trade.

        Parameters
        ----------
        amount : int
            The number of shares to order.
        limit_price : float, optional
            The limit price for the order. The default is None.

        Returns
        -------
        None. The function will update data.cash and also update data.trade_df

        '''
        # Checking if the limit order has passed. Possibility to default self.limit_passed to True if no limit order has been placed
        if limit_price != None and not self.limit_passed:
            if data.daily_lows[self.symbol].loc[data.current_date] < limit_price < data.daily_highs[self.symbol].loc[data.current_date]:
                self.price = limit_price
                self.limit_passed = True
            else:
                return False

        value_of_order = amount * self.price
        value_space = data.starting_amount - data.value_invested # This is used only if self.able_to_exceed == False

        if amount > 0:
            type_of_order = 'long'
            if not self.able_to_exceed and value_of_order > value_space:
                amount = floor(value_space/self.price) # Recalculates the amount to place an order for
                value_of_order = amount * self.price
        elif amount < 0:
            type_of_order = 'short'
            if not self.able_to_exceed and abs(value_of_order) > value_space:
                amount = ceil(-value_space/self.price) # Recalculates the amount to place an order for
                value_of_order = amount * self.price
        if -10 <= amount <= 10:
            return False

        data.trade_df = data.trade_df.append({
            'long_or_short': type_of_order,
            'symbol': self.symbol,
            'open_date': data.current_date,
            'open_price': self.price,
            'open_value': value_of_order,
            'amount': amount,
            'open_reason': self.open_reason,
            'close_reason': self.close_reason},
        ignore_index=True) # Updating the trade dataframe for the new order

        data.positions_tracker.at[data.current_date, self.symbol] = self.current_number_of_shares + amount # Adding the number of shares held of this position on this day
        data.current_positions.add(self.symbol) # NOTE: This will not work if you are using a non-target function to sell shares!
        data.cash -= abs(value_of_order) # Removing the value of the order from our cash. Notice it does not add anything in for short orders
        data.value_invested += abs(value_of_order) # Increasing the value of our total open positions

        return True

    def order_value(self, value, limit_price=None):
        '''
        Places an order for a set value of shares.

        An order for a given stock is placed and added to data.trade_df. If a
        limit order is entered, then the function will ensure the price hits the
        limit order on this day before entering. The entry price will be the
        limit price in this scenario.

        Parameters
        ----------
        value : float
            The value of shares you want to place an order for.
        limit_price : float, optional
            Price to put a limit order in at. The default is None.

        Returns
        -------
        None. The function will update data.cash, data.trade_df,
        data.current_positions, and data.value_invested.

        Examples
        --------
        >>> Orders('ABC').order_value(10000)
        Places an order of $10000 shares of ABC. The trade list will be updated
        to represent this.

        '''
        # Checking if the limit order has passed. Possibility to default self.limit_passed to True if no limit order has been placed
        if limit_price != None and not self.limit_passed:
            if data.daily_lows[self.symbol].loc[data.current_date] < limit_price < data.daily_highs[self.symbol].loc[data.current_date]:
                self.price = limit_price
                self.limit_passed = True
            else:
                return False
        # Below we calculate the number of shares to purchase based on the vlaue of the order
        # Note that these calculations ensure that the order will not exceed the value
        if value > 0:
            amount = floor(value/self.price)
        elif value < 0:
            amount = ceil(value/self.price)
        else:
            return False
        return self.order_amount(amount) # Places an order for the calculated number of shares

    def order_percent(self, percent, limit_price=None):
        '''
        Orders a percent of your starting cash.

        Places an order for a given percent of your starting cash. If compound
        is set to true, will instead use percent of your current wealth. This
        places a fixed order of a value which will be calculated in the functions
        and should not be used to close order. If the value is negative then a
        short order will be placed.

        Parameters
        ----------
        percent : float
            Must be less than or equal to 1. The percent of your portfolio to
            allocate to this order.
        limit_price : float, default None
            Price to put a limit order in at.

        Returns
        -------
        None. The function will update data.cash and also update data.trade_df

        Examples
        --------
        >>> Orders('SPY').order_percent(0.1)

        Will order 10% of your starting cash. If you started with $10000, you
        will order $1000 of SPY

        >>> Orders('AAPL', compound=True).order_percent(-0.05)

        Will place a short order 5% of your current wealth.

        '''
        # Checking if the limit order has passed. Possibility to default self.limit_passed to True if no limit order has been placed
        if limit_price != None and not self.limit_passed:
            if data.daily_lows[self.symbol].loc[data.current_date] < limit_price < data.daily_highs[self.symbol].loc[data.current_date]:
                self.price = limit_price
                self.limit_passed = True
            else:
                return False
        # Note below that self.capital will be the starting amount if self.compound == False
        value = percent * self.capital # Calclulating the value of the order based on the percent
        return self.order_value(value)

    def order_target_amount(self, target_amount, limit_price=None):
        '''
        Orders a number of shares of a stock.

        Will put an order in for a target amount of shares. If negative, will
        place a short order.

        Parameters
        ----------
        target_amount : int
            The desired amount of shares to hold for the stock.
        limit_price : float, default None
            Price to put a limit order in at.

        Returns
        -------
        None. The function will update data.cash and also update data.trade_df

        Examples
        -------
        >>> Orders('SPY').order_target_amount(50)

        This places an order such that you will own 50 shares of SPY at the
        close of today.

        >>> Orders('IEF').order_target_amount(0)

        This will ensure that you will exit all positions of IEF at the close
        of the day

        >>> Orders('SPY', open_reason='Entry 1').order_target_amount(-100, limit_order=101.3)

        This will ensure you are short 100 shares of SPY if the limit price of
        $101.3 is hit on that day.
        '''
        # Checking if the limit order has passed. Possibility to default self.limit_passed to True if no limit order has been placed
        if limit_price != None and not self.limit_passed:
            if data.daily_lows[self.symbol].loc[data.current_date] < limit_price < data.daily_highs[self.symbol].loc[data.current_date]:
                self.price = limit_price
                self.limit_passed = True
            else:
                return False
        if (target_amount > self.current_number_of_shares >= 0) or (target_amount < self.current_number_of_shares <= 0): # Either going more long or more short
            amount_to_order = target_amount - self.current_number_of_shares
            if abs(amount_to_order) < self.min_to_enter:
                return False
            else:
                return self.order_amount(amount_to_order)
        elif self.current_number_of_shares > target_amount >= 0 or self.current_number_of_shares < target_amount <= 0: # Remaining long/short but closing some shares
            amount_to_close = self.current_number_of_shares - target_amount
            amount_left = self.current_number_of_shares - amount_to_close
            data.positions_tracker.at[data.current_date, self.symbol] = amount_left
            if amount_left == 0:
                data.current_positions.remove(self.symbol)
            for index, row in self.all_open_trade_rows.iterrows():
                if abs(amount_to_close) >= abs(row['amount']):
                    self._fully_close_row(trade_number=index)
                    amount_to_close -= row['amount']
                elif abs(amount_to_close) < abs(row['amount']):
                    self._part_close_row(trade_number=index, amount_to_close=amount_to_close)
                elif amount_to_close == 0:
                    break
        elif self.current_number_of_shares > 0 > target_amount or self.current_number_of_shares < 0 < target_amount:
            for index, row in self.all_open_trade_rows.iterrows():
                self._fully_close_row(trade_number=index)
            return self.order_amount(target_amount)
        else:
            return False

    def order_target_value(self, target_value, limit_price=None):
        '''
        Orders a specified value of shares of a stock.

        Will put an order in for a target value of shares. If negative, will
        place a short order.

        Parameters
        ----------
        target_value : float
            The desired value of shares to hold for the stock.
        limit_price : float, default None
            Price to put a limit order in at

        Returns
        -------
        None. The function will update data.cash and also update data.trade_df

        Examples
        -------
        >>> Orders('SPY').order_target_value(5000)

        This places an order such that you will own as close to $5000 worth of
        SPY as possible at the close of today.

        >>> Orders('IEF').order_target_value(0)

        This will ensure that you will exit all positions of IEF at the close
        of the day

        >>> Orders('SPY', open_reason='Entry 1').order_target_value(-10000, limit_order=101.3)

        This will ensure you are short 100 shares of SPY if the limit price of
        $101.3 is hit on that day. The open_reason column in data.trade_df will
        say 'Entry 1' for this trade.
        '''

        # Checking if the limit order has passed. Possibility to default self.limit_passed to True if no limit order has been placed
        if limit_price != None and not self.limit_passed:
            if data.daily_lows[self.symbol].loc[data.current_date] < limit_price < data.daily_highs[self.symbol].loc[data.current_date]:
                self.price = limit_price
                self.limit_passed = True
            else:
                return False
        if target_value >= 0:
            target_amount = floor(target_value/self.price)
        elif target_value < 0:
            target_amount = ceil(target_value/self.price)
        return self.order_target_amount(target_amount)

    def order_target_percent(self, target_percent, limit_price=None):
        '''
        Will put an order in for a target percent of your portfolio. If
        negative, will place a short order.

        Parameters
        ----------
        target_percent : float
            The desired percent of your portfolio to allocate (should be less
            than or equal to 1).
        limit_price : float, default None
            Price to put a limit order in at.

        Returns
        -------
        None. The function will update data.cash and also update data.trade_df

        Examples
        --------
        >>> Orders('SPY').order_target_percent(0.05)

        This places an order such that you will own as close to 5% of your
        starting amount worth of SPY as possible at the close of today.

        >>> Orders('IEF').order_target_percent(0)

        This will ensure that you will exit all positions of IEF at the close
        of the day

        >>> Orders('SPY', open_reason='Entry 1', compund=True).order_target_percent(-0.1, limit_order=101.3)

        This will ensure you are short in SPY at a value as close to 10% of your
        current wealth if the limit price of $101.3 is hit on that day. The
        open_reason column in data.trade_df will say 'Entry 1' for this trade.
        '''
        # Checking if the limit order has passed. Possibility to default self.limit_passed to True if no limit order has been placed
        if limit_price != None and not self.limit_passed:
            if data.daily_lows[self.symbol].loc[data.current_date] < limit_price < data.daily_highs[self.symbol].loc[data.current_date]:
                self.price = limit_price
                self.limit_passed = True
            else:
                return False
        target_value = (target_percent) * self.capital
        return self.order_target_value(target_value)

    def _fully_close_row(self, trade_number):
        row_to_close = data.trade_df.loc[trade_number]
        if row_to_close['symbol'] != self.symbol:
            print('ROW NOT CLOSED AS IT WAS A DIFFERENT SYMBOL')
            return
        amount_before_exit = row_to_close['amount']
        close_value = amount_before_exit * self.price
        profit = close_value - row_to_close['open_value']
        # if data.optimising:
        #     data.trade_df.drop(trade_number, inplace=True)
        # else:
        data.trade_df.at[trade_number, 'close_date'] = data.current_date
        data.trade_df.at[trade_number, 'close_price'] = self.price
        data.trade_df.at[trade_number, 'close_value'] = close_value
        data.trade_df.at[trade_number, 'close_reason'] = self.close_reason
        data.trade_df.at[trade_number, 'profit'] = profit

        data.cash += profit + abs(row_to_close['open_value'])
        data.value_invested -= abs(row_to_close['open_value'])

    def _part_close_row(self, trade_number, amount_to_close):
        row_to_close = data.trade_df.loc[trade_number]
        amount_remaining = row_to_close['amount'] - amount_to_close
        # row_to_add = pd.Series({
        #     'long_or_short': row_to_close['long_or_short'],
        #     'symbol': row_to_close['symbol'],
        #     'open_date': row_to_close['open_date'],
        #     'open_price': row_to_close['open_price'],
        #     'amount': amount_remaining,
        #     'open_value': row_to_close['open_price'] * amount_remaining,
        #     },
        #     name=data.trade_df.index[-1]+1)
        # data.trade_df = data.trade_df.append(row_to_add)
        new_open_value = row_to_close['open_price'] * amount_to_close
        profit = (amount_to_close * self.price) - new_open_value
        # if data.optimising:
        #     data.trade_df.drop(trade_number, inplace=True)
        # else:
        data.trade_df.at[trade_number, 'amount'] = amount_to_close
        data.trade_df.at[trade_number, 'open_value'] = new_open_value
        data.trade_df.at[trade_number, 'close_date'] = data.current_date
        data.trade_df.at[trade_number, 'close_price'] = self.price
        data.trade_df.at[trade_number, 'close_value'] = amount_to_close * self.price
        data.trade_df.at[trade_number, 'close_reason'] = self.close_reason
        data.trade_df.at[trade_number, 'profit'] = profit

        data.cash += profit + abs(new_open_value)
        data.value_invested -= abs(new_open_value)


        data.trade_df = data.trade_df.append({
            'long_or_short': row_to_close['long_or_short'],
            'symbol': row_to_close['symbol'],
            'open_date': row_to_close['open_date'],
            'open_price': row_to_close['open_price'],
            'amount': amount_remaining,
            'open_value': row_to_close['open_price'] * amount_remaining,
            'open_reason': row_to_close['open_reason']
            },
            ignore_index=True)

    def check_stop_loss(self,
                        stop_loss_percent,
                        close_if_hit=True,
                        trade_number=None,
                        eod=False):
        '''
        Checks to see if a stop loss of a stock is hit on this day.

        Parameters
        ----------
        stop_loss_percent : float
            The stop-loss value you wish to set. Usually is between 0 and 1.
        close_if_hit : bool, default True
            If the stop loss is hit, the trades are automatically closed.
        trade_number : int, default None
            Set to the specific number in the trade list of the trade you wish
            to check.
        eod : bool, default False
            If you wish to only check for a hit stop loss on close data.
            Otherwise the stop loss will be triggered if the price hits the stop
            loss at any time.

        Returns
        -------
        bool
            Will return True if the stop-loss is hit, otherwise it will return
            False.

        Examples
        -------
        >>> Orders('SPY', close_reason='stop-loss').check_stop_loss(0.05)
        True (if the value of your positions in SPY drop by 5% in this day)

        '''
        if eod:
            todays_close = data.daily_closes[self.symbol].loc[data.current_date]
            if trade_number == None:
                entry_value = self.all_open_trade_rows['open_value'].sum()
                eod_value = self.current_number_of_shares * todays_close
                if self.all_open_trade_rows['long_or_short'].iloc[0] == 'long':
                    stop_value = (1 - stop_loss_percent) * entry_value
                else:
                    stop_value = (1 + stop_loss_percent) * entry_value
                if eod_value < stop_value:
                    if close_if_hit:
                        self.order_target_amount(0)
                    return True
                else:
                    return False
            else:
                trade_row = data.trade_df.loc[trade_number]
                entry_value = trade_row['open_value']
                number_of_shares = trade_row['amount']
                eod_value = number_of_shares * todays_close
                if trade_row['long_or_short'] == 'long':
                    stop_value = (1 - stop_loss_percent) * entry_value
                else:
                    stop_value = (1 + stop_loss_percent) * entry_value

                if eod_value < stop_value:
                    if close_if_hit:
                        self.fully_close_row(trade_number)
                    return True
                else:
                    return False

        else:
            todays_low = data.daily_lows[self.symbol].loc[data.current_date]
            todays_high = data.daily_highs[self.symbol].loc[data.current_date]
            if trade_number == None:
                entry_value = self.all_open_trade_rows['open_value'].sum()
                # stop_value = (1 - stop_loss_percent) * entry_value
                if self.all_open_trade_rows['long_or_short'].iloc[0] == 'long':
                    min_value_today = self.current_number_of_shares * todays_low
                    stop_value = (1 - stop_loss_percent) * entry_value
                else:
                    min_value_today = self.current_number_of_shares * todays_high
                    stop_value = (1 + stop_loss_percent) * entry_value

                if min_value_today < stop_value: # Same for long or short
                    # print('Exit all')
                    stop_price = stop_value / self.current_number_of_shares
                    if todays_low < stop_price < todays_high:
                        exit_price = stop_price
                    else:
                        exit_price = data.daily_opens[self.symbol].loc[data.current_date]
                    if close_if_hit:
                        self.order_target_amount(0, limit_price=exit_price)
                    return True
                else:
                    return False

            else:
                trade_row = data.trade_df.loc[trade_number]
                entry_value = trade_row['open_value']
                number_of_shares = trade_row['amount']
                # stop_value = (1 - stop_loss_percent) * entry_value
                if trade_row['long_or_short'] == 'long':
                    min_value_today = number_of_shares * todays_low
                    stop_value = (1 - stop_loss_percent) * entry_value
                else:
                    min_value_today = number_of_shares * todays_high
                    stop_value = (1 + stop_loss_percent) * entry_value

                if min_value_today < stop_value:
                    stop_price = stop_value / number_of_shares
                    if todays_low < stop_price < todays_high:
                        exit_price = stop_price
                    else:
                        exit_price = data.daily_opens[self.symbol].loc[data.current_date]
                    if close_if_hit:
                        self._fully_close_row(trade_number)
                    return True
                else:
                    return False




def get_norgatedata(symbol_list,
                    start_date=date(2000,1,1),
                    end_date=datetime.now().date(),
                    fields=['Close'],
                    start_when_all_are_in=True,
                    adjustment='TotalReturn',
                    progress_desc='Downloading Norgate Data'):
    '''
    Downloads data from NorgateData.

    Creates dataframes of norgate data for the symbols provided. The dataframes
    are stored in data.

    Parameters
    ----------
    symbol_list : list
        A list containing all the symbols of data to be gathered.
    start_date : datetime, default date(2000,1,1)
        The start date you wish to get data from.
    end_date : datetime, default date(2020,1,2)
        The end date you wish to get data to.
    fields: list, default ['Close']
        A list of the fields you wish to download. Must contain any combination
        of {'Open', 'High', 'Low', 'Close', 'Volume', 'Turnover', 'Unadjusted
        Close'}.
    start_when_all_are_in : bool, default True.
        Determines whether or not to drop all dates that do not contain any
        data for the stocks. If set to True, will drop the dates that any
        stock is missing data.
    adjustment : {'TotalReturn', 'Capital', 'None'}, default 'TotalReturn'.
        The type of adjustment desired for the data.
    progress_desc : str, default 'Downloading Norgate Data'
        The message you would like to appear in the progress bar while data is
        downloading.

    Returns
    -------
    None. The data stored in data.daily_{opens, highs, lows, closes, volumes,
    turnovers}

    Examples
    --------
    '''
    all_dates = pd.date_range(start=start_date, end=end_date)
    if adjustment == 'TotalReturn':
        priceadjust = norgatedata.StockPriceAdjustmentType.TOTALRETURN
    elif adjustment == 'None':
        priceadjust = norgatedata.StockPriceAdjustmentType.NONE
    elif adjustment == 'Capital':
        priceadjust = norgatedata.StockPriceAdjustmentType.CAPITAL
    padding_setting = norgatedata.PaddingType.NONE
    timeseriesformat = 'pandas-dataframe'
    start_date = pd.to_datetime(start_date, format='%Y-%m-%d')
    end_date = pd.to_datetime(end_date, format='%Y-%m-%d')
    need_close = 'Close' in fields
    need_open = 'Open' in fields
    need_high = 'High' in fields
    need_low = 'Low' in fields
    need_volume = 'Volume' in fields
    need_turnover = 'Turnover' in fields
    need_unadjustedclose = 'Unadjusted Close' in fields
    if need_close:
        daily_closes = pd.DataFrame(index=all_dates)
    if need_open:
        daily_opens = pd.DataFrame(index=all_dates)
    if need_high:
        daily_highs = pd.DataFrame(index=all_dates)
    if need_low:
        daily_lows = pd.DataFrame(index=all_dates)
    if need_volume:
        daily_volumes = pd.DataFrame(index=all_dates)
    if need_turnover:
        daily_turnovers = pd.DataFrame(index=all_dates)
    if need_unadjustedclose:
        daily_unadjustedcloses = pd.DataFrame(index=all_dates)
    pbar = tqdm(total=len(symbol_list), position=0, desc=progress_desc)
    for symbol in symbol_list:
        pricedata_dataframe = norgatedata.price_timeseries(
        symbol,
        stock_price_adjustment_setting = priceadjust,
        padding_setting = padding_setting,
        start_date = start_date,
        end_date = end_date,
        format=timeseriesformat,
        fields=fields
        )
        if need_close:
            daily_closes[symbol] = pricedata_dataframe['Close']
        if need_open:
            daily_opens[symbol] = pricedata_dataframe['Open']
        if need_high:
            daily_highs[symbol] = pricedata_dataframe['High']
        if need_low:
            daily_lows[symbol] = pricedata_dataframe['Low']
        if need_volume:
            daily_volumes[symbol] = pricedata_dataframe['Volume']
        if need_turnover:
            daily_turnovers[symbol] = pricedata_dataframe['Turnover']
        if need_unadjustedclose:
            daily_unadjustedcloses[symbol] = pricedata_dataframe['Unadjusted Close']
        pbar.update(1)
    pbar.close()

    if need_close:
        daily_closes = daily_closes.dropna(how='all')
        daily_closes = daily_closes.fillna(method='ffill') + (daily_closes.fillna(method='bfill') * 0)
        if start_when_all_are_in:
            daily_closes = daily_closes.dropna(how='any')
        data.daily_closes = daily_closes

    if need_open:
        daily_opens = daily_opens.dropna(how='all')
        daily_opens = daily_opens.fillna(method='ffill') + (daily_opens.fillna(method='bfill') * 0)
        if start_when_all_are_in:
            daily_opens = daily_opens.dropna(how='any')
        data.daily_opens = daily_opens

    if need_high:
        daily_highs = daily_highs.dropna(how='all')
        daily_highs = daily_highs.fillna(method='ffill') + (daily_highs.fillna(method='bfill') * 0)
        if start_when_all_are_in:
            daily_highs = daily_highs.dropna(how='any')
        data.daily_highs = daily_highs

    if need_low:
        daily_lows = daily_lows.dropna(how='all')
        daily_lows = daily_lows.fillna(method='ffill') + (daily_lows.fillna(method='bfill') * 0)
        if start_when_all_are_in:
            daily_lows = daily_lows.dropna(how='any')
        data.daily_lows = daily_lows

    if need_volume:
        daily_volumes = daily_volumes.dropna(how='all')
        daily_volumes = daily_volumes.fillna(method='ffill') + (daily_volumes.fillna(method='bfill') * 0)
        if start_when_all_are_in:
            daily_volumes = daily_volumes.dropna(how='any')
        data.daily_volumes = daily_volumes

    if need_turnover:
        daily_turnovers = daily_turnovers.dropna(how='all')
        daily_turnovers = daily_turnovers.fillna(method='ffill') + (daily_turnovers.fillna(method='bfill') * 0)
        if start_when_all_are_in:
            daily_turnovers = daily_turnovers.dropna(how='any')
        data.daily_turnovers = daily_turnovers

    if need_unadjustedclose:
        daily_unadjustedcloses = daily_unadjustedcloses.dropna(how='all')
        daily_unadjustedcloses = daily_unadjustedcloses.fillna(method='ffill') + (daily_unadjustedcloses.fillna(method='bfill') * 0)
        if start_when_all_are_in:
            daily_unadjustedcloses = daily_unadjustedcloses.dropna(how='any')
        data.daily_unadjustedcloses = daily_unadjustedcloses

    if need_close:
        data.all_dates = daily_closes.index
    elif need_open:
        data.all_dates = daily_opens.index
    elif need_high:
        data.all_dates = daily_highs.index
    elif need_low:
        data.all_dates = daily_lows.index
    elif need_volume:
        data.all_dates = daily_volumes.index
    elif need_turnover:
        data.all_dates = daily_turnovers.index
    else:
        print('The error occured because no OHL or C was selected')

def get_csv_data(folder_path,
                 data_format='combined',
                 start_date=date(2000,1,1),
                 end_date=datetime.now().date(),
                 start_when_all_are_in=True):
    '''Short summary.

    Parameters
    ----------
    folder_path : type
        Description of parameter `folder_path`.
    format : type
        Description of parameter `format`.
    start_date : type
        Description of parameter `start_date`.
    end_date : type
        Description of parameter `end_date`.
    start_when_all_are_in : type
        Description of parameter `start_when_all_are_in`.

    Returns
    -------
    type
        Description of returned object.

    '''
    all_files = {fname[:-4]: pd.read_csv(folder_path+'\\'+fname, index_col=0, parse_dates=True) for fname in os.listdir(folder_path)}
    if data_format == 'combined':
        for fname, daily_data in all_files.items():
            daily_data = daily_data.loc[start_date:end_date]
            if start_when_all_are_in:
                daily_data.dropna(how='any')
            else:
                daily_data.dropna(how='all')
            exec('data.{} = daily_data'.format(fname))
        try:
            data.all_dates = data.daily_closes.index
        except AttributeError:
            raise NameError('ensure there is a daily_closes.csv in the source path.')


def get_valid_dates(max_lookback=200,
                    rebalance='daily',
                    start_trading = None,
                    end_trading = None):
    '''
    Generates a date list containing the dates you wish to trade on. Considers
    the NYSE trading calendar.

    Parameters
    ----------
    max_lookback : int, optional
        The maximum lookback needed for your backtest. The default is 200.
    rebalance : {'daily', 'weekly', 'month-end', 'month-start'}, default 'daily'
        The frequency you wish to rebalance your portfolio. You have a choice
        of 'daily', 'weekly', 'month-end' or 'month-start'.

    Raises
    ------
    ValueError
        If the rebalance is not 'daily', 'weekly' or 'month-end' or 'month-start'.

    Returns
    -------
    new_date_list : list
        A list containing all valid dates that can be traded on at the desired
        rebalance frequency.

    '''
    all_dates = data.all_dates[max_lookback:]

    if start_trading != None:
        start = start_trading
    else:
        start = all_dates[0]
    if end_trading != None:
        end = end_trading
    else:
        end = all_dates[-1]

    nyse = mcal.get_calendar('NYSE')
    all_valid_dates = nyse.valid_days(start_date=start, end_date=end)

    if rebalance == 'month-end':
        date_list = (all_dates + pd.offsets.BMonthEnd()).drop_duplicates()
    elif rebalance == 'month-start':
        date_list = (all_dates + pd.offsets.BMonthBegin()).drop_duplicates()
    elif rebalance == 'weekly':
        date_list = (all_dates + pd.offsets.Week(n=0, weekday=4)).drop_duplicates()
    elif rebalance == 'daily':
        date_list = all_dates
    else:
        raise ValueError('rebalance must be either "daily", "weekly", "month-end", or "month-start"')

    new_date_list = []
    for ind in range(len(date_list)):
        new_date = date_list[ind]
        if new_date < all_valid_dates[0].date():
            continue
        while new_date not in all_valid_dates:
            new_date -= timedelta(days=1)
        new_date_list.append(new_date)

    if end_trading != None:
        final_index = data.all_dates.get_loc(new_date_list[-1])
        data.all_dates = data.all_dates[:final_index]

    return new_date_list

def initialise():
    '''
    Resets all variables before beginning a new backtest.

    Sets data.start_date to the first tradeable data based on data.daily_closes
    and max_lookback.
    Sets data.positions_tracker to an empty dataframe with column headers equal
    to all stocks in the universe in use.
    Sets data.current_date to data.start_date.
    Sets data.current_price to data.daily_closes on the current date.
    Sets data.wealth track to an empty list.
    Sets data.date_track to an empty list.
    Sets data.cash to data.starting_amount.
    Sets data.wealth to data.starting_amount.
    Sets data.value_invested to 0
    Recreates data.trade_df with the appropriate column headers.


    Returns
    -------
    None.

    '''
    data.start_date = data.all_dates[0]
    data.positions_tracker = pd.DataFrame(index=data.daily_closes.index, columns=data.daily_closes.columns)
    data.current_date = data.start_date
    data.current_price = data.daily_closes.loc[data.current_date]

    data.wealth_track = []
    data.date_track = []
    data.current_positions = set()
    #data.starting_amount = 100000
    data.cash = data.starting_amount
    data.wealth = data.starting_amount
    data.value_invested = 0

    columns = ['long_or_short', 'symbol', 'open_date', 'open_price', 'amount',
               'open_value','open_reason', 'close_date', 'close_price',
               'close_value', 'close_reason', 'profit']
    data.trade_df = pd.DataFrame(columns=columns)

def update():
    '''
    Call this function at the end of each day of the backtest to calculate the
    current equity of that day.

    Returns
    -------
    None.

    '''
    total_wealth = data.cash
    all_open_trade_rows = data.trade_df[data.trade_df['close_price'].isnull()]
    current_position_value = 0
    for index, row in all_open_trade_rows.iterrows():
        current_value = row['amount'] * data.current_price[row['symbol']]
        if row['long_or_short'] == 'long':
            current_position_value += current_value
        else:
            current_position_value -= (2 * row['open_value']) - current_value
    total_wealth += current_position_value
    data.wealth_track.append(total_wealth)
    data.date_track.append(data.current_date)
    if data.optimising:
        all_closed_rows = data.trade_df[data.trade_df['close_price'].isnull()==False]
        data.trade_df.drop(all_closed_rows.index, inplace=True)
        data.trade_df.reset_index(drop=True, inplace=True)


def plot_results(benchmark=None,
                 start_date=date(2000,1,3),
                 end_date=datetime.now().date(),
                 title=None,
                 date_format='%d/%m/%Y',
                 equity_label='OpenEquity'):
    '''
    Produces a plotly plot that automatically opens in the default browser.

    Parameters
    ----------
    benchmark : str, default None
        The file location of an equity series that can be plotted on the same
        graph as the backtest result. Must have the column header 'equity'.
    start_date : datetime, default date(200,1,3)
        The start date of the plot.
    end_date : datetime, defaul date(2019,12,31)
        The end date of the plot.
    title : str, default None
        The title which will appear at the top of the plot.

    Notes
    -----
    Look in to the ability to plot drawdown and other useful plots. Look at
    tradestation for various useful graphs.

    '''
    wealth_list = [x - 100000 for x in data.wealth_track]
    equity_df = pd.DataFrame(columns=['date', 'equity'])
    equity_df['date'] = data.date_track
    equity_df['equity'] = wealth_list
    equity_df.set_index('date', inplace=True)
    equity_df = equity_df.loc[start_date:end_date]
    equity_df['equity'] = equity_df['equity'] - equity_df['equity'].iloc[0]

    fig = go.Figure([go.Scatter(x=equity_df.index, y=equity_df['equity'], name='My Strategy')])
    if benchmark != None:
        comparison_DW = pd.read_csv(benchmark, index_col=0)
        comparison_DW.index = pd.to_datetime(comparison_DW.index, format=date_format)
        comparison_DW = comparison_DW.loc[start_date:end_date]
        comparison_DW[equity_label] = comparison_DW[equity_label] - comparison_DW[equity_label].iloc[0]
        fig.add_trace(go.Scatter(x=comparison_DW.index, y=comparison_DW[equity_label], name='Benchmark results'))
    fig.update_layout(template='plotly_dark', title=title)
    plot(fig, auto_open=True)
