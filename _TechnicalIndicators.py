# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 14:35:34 2020

@author: User
"""

import pandas as pd
from tqdm import tqdm
import numpy as np
from math import sqrt

def RSI(prices, n=14):
    '''
    Calculates all RSI_values for a given lookback period and produces a
    pandas dataframe with the values linked to the dates they occured.

    Parameters
    ----------
    prices : pandas-dataframe
        A dataframe of the values for RSIs to be calculated on.
    n : int, optional
        The lookback length for RSI calculations. The default is 14.

    Returns
    -------
    total_RSI : pandas-dataframe
        Dataframe containing RSI calculations for each stock on each date.
    '''
    SF = 1/n
    total_RSI = pd.DataFrame(index=prices.index, columns=prices.columns)
    pbar = tqdm(total=len(prices.columns), position=0, desc='Calculating RSIs')
    for stock in prices.columns:
        NetChgAvg = 0
        TotChgAvg = 0
        stock_series = prices[stock].dropna()
        all_RSI = pd.DataFrame(index=stock_series.index, columns=[stock_series.name])
        for i in range(len(stock_series)):
            if i > n:
                Change = stock_series.iloc[i] - stock_series.iloc[i-1]
                NetChgAvg = NetChgAvg + (SF * (Change - NetChgAvg))
                TotChgAvg = TotChgAvg + (SF * (abs(Change) - TotChgAvg))
            elif i < n:
                pass
            elif i == n:
                prices_n = stock_series.iloc[i-n:i]
                NetChgAvg = prices_n.iloc[-1] - prices_n.iloc[0]
                diff = prices_n.diff().abs()
                TotChgAvg = diff.mean()
                
            if TotChgAvg != 0:
                ChgRatio = NetChgAvg / TotChgAvg
            else:
                ChgRatio = 0
                
            RSI = 50 * (ChgRatio + 1)
            all_RSI[stock_series.name].iloc[i] = RSI
        total_RSI[stock] = all_RSI
        pbar.update(1)
    pbar.close()
        
    return total_RSI

def RSI_new(prices, n=14):
    delta = prices.diff()
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    
    roll_up = up.ewm(alpha=1/n, min_periods=n).mean()
    roll_down = down.abs().ewm(alpha=1/n, min_periods=n).mean()
    
    RS = roll_up / roll_down
    RSI = 100 - (100 / (1 + RS))
    return RSI
    

def SKEW(prices, n=10):
    '''
    Calculates current skewness of a single stock.

    Parameters
    ----------
    prices : pandas-series
        A series of the values for skewness to be calculated on, with the last
        value being the current price in the backtest.
    n : int, optional
        The lookback length for skewness calculations. The default is 10.

    Returns
    -------
    float
        the skewness value for the current date with the given lookback.

    '''
    prices = prices.iloc[-n:]
    m = prices.mean()
    sdev = prices.std()
    if sdev > 0:
        s = 0
        for i in range(n):
            s += ((prices.iloc[-i] - m) / sdev)**3
        y = n / ((n-1) * (n-2))
    return y * s
            
def KURTOSIS(prices, n=10):
    '''
    Calculates kurtosis of a single stock.

    Parameters
    ----------
    prices : pandas-series
        A series where the last value is the current days price in the
        backtest.
    n : int, optional
        The lookback period for the value to be calculated. The default is 10.

    Raises
    ------
    ValueError
        If n is less than or equal to 3.

    Returns
    -------
    float
        The value of kurtosis over the lookback period. Will return 0 if the
        standard deviation of the given prices is negative

    '''
    if n <= 3:
        raise ValueError('Kurtosis Length must be greater than 3')
        return None
    prices = prices[-n:]
    m = prices.mean()
    sdev = prices.std()
    if sdev > 0:
        p2 = 0
        for value1 in range(n):
            p2 += ((prices.iloc[-value1] - m) / sdev)**4
        p1 = n * (n+1) / ((n-1) * (n-2) * (n-3))
        p3 = 3 * ((n-1))**2 / ((n-2) * (n-3))
        return p1 * p2 - p3
    else:
        return 0
     
def HistoricVolatility(prices, n=100):
    '''
    Calculates all annualised volatility values of a given price set.

    Parameters
    ----------
    prices : pandas-dataframe
        A price-series dataframe with stock symbols as column headers.
    n : int, optional
        The lookback period for volatility to be calculated. The default is
        100.

    Returns
    -------
    pandas-dataframe
        A datframe with the calculated historic volatilities with the given
        lookback. The first n rows will be NaN as they are needed to gain
        enough information for a sufficient lookback.

    '''
    return np.log(1 + prices.pct_change()).rolling(n).std() * sqrt(252) * 100

def HighestHigh(prices, n=5):
    '''
    Takes a time-series dataframe and checks whether the current value on
    each value in the time-series is the largest over the previous n rows.

    Parameters
    ----------
    prices : pandas-dataframe
        A time series dataframe populated with price values.
    n : int, optional
        A lookback period to check if each value is the highest over the past
        n values. The default is 5.

    Returns
    -------
    pandas-dataframe
        Dataframe populated with boolean values. True if the cell is the
        highest over the n-1 cells before (as n includes the current one).

    '''
    return prices.rolling(n).max() == prices

def TrueRangeCustom(Highs, Lows, Closes):
    '''
    Similar to the TradeStation function. Only used in the process of
    calculating ADX values.

    Parameters
    ----------
    Highs : pandas-dataframe
        Time-series dataframe with the highs of each day of multiple stocks.
    Lows : pandas-dataframe
        Time-series dataframe with the lows of each day of multiple stocks.
    Closes : pandas-dataframe
        Time-series dataframe with the closes of each day of multiple stocks.

    Returns
    -------
    TrueRange_df : pandas-dataframe
        Dataframe containing the custom made true-range values.

    '''
    TrueRange_df = pd.DataFrame(index=Closes.index, columns=Closes.columns)
    pbar = tqdm(total=len(Closes.columns), position=0, desc='Calculating True Ranges')
    for stock in TrueRange_df.columns:
        stock_df = pd.DataFrame()
        stock_df['High'] = Highs[stock]
        stock_df['Low'] = Lows[stock]
        stock_df['Close'] = Closes[stock]
        stock_df.dropna(inplace=True)
        
        all_true_range = pd.Series(index=stock_df.index)
        for i in range(1, len(stock_df)):
            THigh = stock_df['High'].iloc[i]
            TLow = stock_df['Low'].iloc[i]
            close_before = stock_df['Close'].iloc[i-1]
            if close_before > stock_df['High'].iloc[i]:
                THigh = close_before
            elif close_before < stock_df['Low'].iloc[i]:
                TLow = close_before
            all_true_range.iloc[i] = THigh - TLow
        TrueRange_df[stock] = all_true_range
        pbar.update(1)
    pbar.close()
    return TrueRange_df

def ADX(Highs, Lows, Closes, length=10):
    '''
    Similar to Tradestation function. Uses the TrueRangeCustom function to
    calculate the ADX values for a time-series prices dataframe

    Parameters
    ----------
    Highs : pandas-dataframe
        Time-series dataframe with the highs of each day for multiple stocks.
    Lows : pandas-dataframe
        Time-series dataframe with the lows of each day for multiple stocks.
    Closes : pandas-dataframe
        Time-series dataframe with the closes of each day for multiple stocks.
    length : int, optional
        Lookback length for the ADX values. The default is 10.

    Returns
    -------
    ADX_df : pandas-dataframe
        Time-series dataframe with the calculated ADX values. The first
        'length' values will be NaN.

    '''
    TrueRange_df = TrueRange(Highs, Lows, Closes) # Was originally TrueRangeCustom, but am changing it to TrueRange to test
    SF = 1/length
    ADX_df = pd.DataFrame(index=Closes.index, columns=Closes.columns)
    pbar = tqdm(total=len(ADX_df.columns), position=0, desc='Calculating ADX values')
    for stock in ADX_df.columns:
        stock_TR = TrueRange_df[stock]
        PriceH = Highs[stock].dropna()
        PriceL = Lows[stock].dropna()
        PriceC = Closes[stock].dropna()
        all_ADX = pd.Series(index=PriceC.index)
        
        sumPlusDM = 0
        sumMinusDM = 0
        sumTR = 0
        oDMIsum = 0
        oADX = 0
        for i in range(len(PriceC)):
            if i == length:
                for value1 in range(length):
                    PlusDM = 0
                    MinusDM = 0
                    UpperMove = PriceH.iloc[i-value1] - PriceH.iloc[i-value1-1]
                    LowerMove = PriceL[i-value1-1] - PriceL[i-value1]
                    if UpperMove > LowerMove and UpperMove > 0:
                        PlusDM = UpperMove
                    elif LowerMove > UpperMove and LowerMove > 0:
                        MinusDM = LowerMove
                    sumPlusDM += PlusDM
                    sumMinusDM += MinusDM
                    sumTR += stock_TR.loc[PriceC.index[i-value1]]
                AvgPlusDM = sumPlusDM / length
                AvgMinusDM = sumMinusDM / length
                oVolty = sumTR / length
            elif i > length:
                PlusDM = 0
                MinusDM = 0
                UpperMove = PriceH.iloc[i] - PriceH.iloc[i-1]
                LowerMove = PriceL.iloc[i-1] - PriceL.iloc[i]
                if UpperMove > LowerMove and UpperMove > 0:
                    PlusDM = UpperMove
                elif LowerMove > UpperMove and LowerMove > 0:
                    MinusDM = LowerMove
                AvgPlusDM = AvgPlusDM + SF * (PlusDM - AvgPlusDM)
                AvgMinusDM = AvgMinusDM + SF * (MinusDM - AvgMinusDM)
                oVolty = oVolty + SF * (stock_TR.loc[PriceC.index[i]] - oVolty)
            else:
                continue
                
            if oVolty > 0:
                oDMIPlus = 100 * AvgPlusDM / oVolty
                oDMIMinus = 100 * AvgMinusDM / oVolty
            else:
                oDMIPlus = 0
                oDMIMinus = 0
                
            Divisor = oDMIPlus + oDMIMinus
            if Divisor > 0:
                oDMI = 100 * abs(oDMIPlus - oDMIMinus) / Divisor
            else:
                oDMI = 0
                
            if length < i <= length*2:
                oDMIsum += oDMI
                oADX = oDMIsum / (i + 1 - length)
            else:
                oADX = oADX +  SF * (oDMI - oADX)
            
            all_ADX.iloc[i] = oADX
        ADX_df[stock] = all_ADX
        pbar.update(1)
    pbar.close()
    return ADX_df

def TrueHigh(Highs, Closes):
    '''
    Calculates the true high values for time-series data of multiple stocks.
    The true high value is defined as yesterday's close if yesterday's close
    is greater than today's high, and is defined as today's high if today's
    high is greater than yesterday's close.

    Parameters
    ----------
    Highs : pandas-dataframe
        Time-series dataframe with the highs of each day for multiple stocks.
    Closes : pandas-dataframe
        Time-series dataframe with the closes of each day for multiple stocks.

    Returns
    -------
    TH_df : pandas-dataframe
        Time-series dataframe with the true high of each day for multiple
        stocks.

    '''
    TH_df = pd.DataFrame(index=Closes.index, columns=Closes.columns)
    yesterday_closes = Closes.shift(1)
    TH_df[yesterday_closes > Highs] = yesterday_closes
    TH_df[yesterday_closes <= Highs] = Highs
    return TH_df

def TrueLow(Lows, Closes):
    '''
    Calculates the true low values for time-series data of multiple stocks.
    The true low value is defined as yesterday's close if yesterday's close
    is less than today's low, and is defined as today's low if today's
    low is less than yesterday's close.

    Parameters
    ----------
    Lows : pandas-dataframe
        Time-series dataframe with the lows of each day for multiple stocks.
    Closes : pandas-dataframe
        Time-series dataframe with the closes of each day for multiple stocks.

    Returns
    -------
    TL_df : pandas-dataframe
        Time-series dataframe with the true low of each day for multiple
        stocks.

    '''
    TL_df = pd.DataFrame(index=Closes.index, columns=Closes.columns)
    yesterday_closes = Closes.shift(1)
    TL_df[yesterday_closes < Lows] = yesterday_closes
    TL_df[yesterday_closes >= Lows] = Lows
    return TL_df

def TrueRange(Highs, Lows, Closes):
    '''
    Calculates the true range values for time-series data of multiple stocks.
    The true range value is defined as the differnece between the true high
    value and the true low value for each day.

    Parameters
    ----------
    Highs : pandas-dataframe
        Time-series dataframe with the highs of each day for multiple stocks.
    Lows : pandas-dataframe
        Time-series dataframe with the lows of each day for multiple stocks.
    Closes : pandas-dataframe
        Time-series dataframe with the closes of each day for multiple stocks.

    Returns
    -------
    pandas-dataframe
        Time-series dataframe with the true range value of each day for
        multiple stocks.

    '''
    True_Highs = TrueHigh(Highs, Closes)
    True_Lows = TrueLow(Lows, Closes)
    return True_Highs - True_Lows

def AvgTrueRange(Highs, Lows, Closes, length=10, method='simple'):
    '''
    Calculates the average true range values of a time-series dataframe.

    Parameters
    ----------
    Highs : pandas-dataframe
        Time-series dataframe with the highs of each day for multiple stocks.
    Lows : pandas-dataframe
        Time-series dataframe with the lows of each day for multiple stocks.
    Closes : pandas-dataframe
        Time-series dataframe with the closes of each day for multiple stocks.
    length : int, optional
        Lookback period for the average to be taken on. The default is 10.
    method : str, optional
        The method of calculating the average. Can either be 'simple' or
        'wilders' for now.

    Returns
    -------
    pandas-dataframe
        Time-series dataframe with the average true range values for each day
        for each stock. The first 'length' stocks will be NaN.

    '''
    True_Ranges = TrueRange(Highs, Lows, Closes)
    if method == 'simple':
        Avg_True_Ranges = True_Ranges.rolling(length).mean()
    elif method == 'wilders':
        Avg_True_Ranges = True_Ranges.ewm(alpha=1/length, min_periods=length).mean()
    return Avg_True_Ranges
    
    
            
            
            
            
            

            
            
   



























     