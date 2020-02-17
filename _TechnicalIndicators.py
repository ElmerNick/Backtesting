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
    Calculates Relative Strength Index.

    Calculates all the RSI values for time-series data with a given lookback
    using Wilder's smoothing.

    Parameters
    ----------
    prices : pandas-dataframe
        A dataframe populated with price data for any number of stocks.
    n : type, default 14
        The lookback period for RSI calculation.

    Returns
    -------
    pandas-dataframe
        A dataframe with all RSI caluations. The first `n` rows will be NaN.

    Examples
    -------
    >>>df
                    SPY_Closes  AAPL_Closes
    2019-01-02  245.531174   155.214005
    2019-01-03  239.672119   139.753540
    2019-01-04  247.700104   145.719528
    2019-01-07  249.653137   145.395172
    2019-01-08  251.998703   148.166855
    2019-01-09  253.176422   150.682983
    2019-01-10  254.069519   151.164597
    2019-01-11  254.167664   149.680466
    2019-01-14  252.617004   147.429718
    2019-01-15  255.512207   150.447113
    2019-01-16  256.130493   152.285065
    2019-01-17  258.073700   153.189301
    2019-01-18  261.508636   154.132858
    2019-01-22  257.975555   150.673172
    2019-01-23  258.515350   151.282532
    2019-01-24  258.652710   150.083435
    2019-01-25  260.841309   155.056732
    2019-01-28  258.858826   153.621765
    2019-01-29  258.515350   152.029510
    2019-01-30  262.607849   162.418396
    2019-01-31  264.914185   163.588013
    2019-02-01  265.041748   163.666641

    >>>RSI(df, n=3)
                    SPY_Closes  AAPL_Closes
    2019-01-02         NaN          NaN
    2019-01-03         NaN          NaN
    2019-01-04         NaN          NaN
    2019-01-07   73.720741    35.597653
    2019-01-08   80.606633    53.063092
    2019-01-09   83.803064    65.721523
    2019-01-10   86.360271    68.185029
    2019-01-11   86.706242    51.182345
    2019-01-14   54.152828    32.657427
    2019-01-15   77.651635    61.024874
    2019-01-16   80.803434    71.856647
    2019-01-17   88.469598    76.646324
    2019-01-18   94.399664    81.558774
    2019-01-22   52.634631    37.812653
    2019-01-23   56.995042    45.531347
    2019-01-24   58.454890    33.322985
    2019-01-25   77.063521    75.009777
    2019-01-28   47.907319    59.035409
    2019-01-29   43.618567    43.585926
    2019-01-30   78.314627    84.158836
    2019-01-31   85.735172    85.874451
    2019-02-01   86.128969    86.027049
    '''
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
    n : int, default 10
        The lookback length for skewness calculations. The default is 10.

    Returns
    -------
    float
        the skewness value for the current date with the given lookback.

    Examples
    --------
    >>>df
                    SPY_Closes  AAPL_Closes
    2019-01-02  245.531174   155.214005
    2019-01-03  239.672119   139.753540
    2019-01-04  247.700104   145.719528
    2019-01-07  249.653137   145.395172
    2019-01-08  251.998703   148.166855
    2019-01-09  253.176422   150.682983
    2019-01-10  254.069519   151.164597
    2019-01-11  254.167664   149.680466
    2019-01-14  252.617004   147.429718
    2019-01-15  255.512207   150.447113
    2019-01-16  256.130493   152.285065
    2019-01-17  258.073700   153.189301
    2019-01-18  261.508636   154.132858
    2019-01-22  257.975555   150.673172
    2019-01-23  258.515350   151.282532
    2019-01-24  258.652710   150.083435
    2019-01-25  260.841309   155.056732
    2019-01-28  258.858826   153.621765
    2019-01-29  258.515350   152.029510
    2019-01-30  262.607849   162.418396
    2019-01-31  264.914185   163.588013
    2019-02-01  265.041748   163.666641

    >>>SKEW(df['SPY_Closes'], n=10)
    0.7066818016522822
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
        standard deviation of the given prices is negative.

    Examples
    --------
    >>>df
                    SPY_Closes  AAPL_Closes
    2019-01-02  245.531174   155.214005
    2019-01-03  239.672119   139.753540
    2019-01-04  247.700104   145.719528
    2019-01-07  249.653137   145.395172
    2019-01-08  251.998703   148.166855
    2019-01-09  253.176422   150.682983
    2019-01-10  254.069519   151.164597
    2019-01-11  254.167664   149.680466
    2019-01-14  252.617004   147.429718
    2019-01-15  255.512207   150.447113
    2019-01-16  256.130493   152.285065
    2019-01-17  258.073700   153.189301
    2019-01-18  261.508636   154.132858
    2019-01-22  257.975555   150.673172
    2019-01-23  258.515350   151.282532
    2019-01-24  258.652710   150.083435
    2019-01-25  260.841309   155.056732
    2019-01-28  258.858826   153.621765
    2019-01-29  258.515350   152.029510
    2019-01-30  262.607849   162.418396
    2019-01-31  264.914185   163.588013
    2019-02-01  265.041748   163.666641

    >>>KURTOSIS(df['SPY_Closes'], n=10)
    -1.0539330782600977
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
        lookback. The first `n` rows will be NaN as they are needed to gain
        enough information for a sufficient lookback.

    Examples
    --------
    >>>df
    SPY_Closes  AAPL_Closes
    2010-01-04   92.788445    26.538448
    2010-01-05   93.034065    26.584333
    2010-01-06   93.099564    26.161472
    2010-01-07   93.492561    26.113111
    2010-01-08   93.803688    26.286718
    ...                ...          ...
    2019-12-24  321.230011   283.596924
    2019-12-26  322.940002   289.223602
    2019-12-27  322.859985   289.113831
    2019-12-30  321.079987   290.829773
    2019-12-31  321.859985   292.954712
    [2516 rows x 2 columns]

    >>>HistoricVolatility(df, n=4)
                    SPY_Closes  AAPL_Closes
    2010-01-04         NaN          NaN
    2010-01-05         NaN          NaN
    2010-01-06         NaN          NaN
    2010-01-07         NaN          NaN
    2010-01-08    2.365432    15.464532
    ...                ...          ...
    2019-12-24    3.315624    13.080743
    2019-12-26    3.895287    17.195093
    2019-12-27    4.060394    16.336670
    2019-12-30    7.025943    14.528539
    2019-12-31    7.317238    13.302135
    [2516 rows x 2 columns]
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
        highest over the `n-1` cells before (as `n` includes the current one).

    Examples
    --------
    >>>df
                SPY_Closes  AAPL_Closes
    2019-12-02  310.115326   263.534546
    2019-12-03  308.035522   258.835724
    2019-12-04  309.936188   261.120270
    2019-12-05  310.493439   264.951172
    2019-12-06  313.329498   270.069031
    2019-12-09  312.344360   266.288025
    2019-12-10  311.996063   267.844330
    2019-12-11  312.881714   270.128906
    2019-12-12  315.578461   270.817261
    2019-12-13  315.767517   274.498535
    2019-12-16  317.936859   279.197357
    2019-12-17  318.006531   279.746094
    2019-12-18  318.026398   279.077667
    2019-12-19  319.329987   279.356995
    2019-12-20  320.730011   278.778381
    2019-12-23  321.220001   283.327576
    2019-12-24  321.230011   283.596924
    2019-12-26  322.940002   289.223602
    2019-12-27  322.859985   289.113831
    2019-12-30  321.079987   290.829773
    2019-12-31  321.859985   292.954712

    >>>HighestHigh(df, n=5)
                    SPY_Closes  AAPL_Closes
    2019-12-02       False        False
    2019-12-03       False        False
    2019-12-04       False        False
    2019-12-05       False        False
    2019-12-06        True         True
    2019-12-09       False        False
    2019-12-10       False        False
    2019-12-11       False         True
    2019-12-12        True         True
    2019-12-13        True         True
    2019-12-16        True         True
    2019-12-17        True         True
    2019-12-18        True        False
    2019-12-19        True        False
    2019-12-20        True        False
    2019-12-23        True         True
    2019-12-24        True         True
    2019-12-26        True         True
    2019-12-27       False        False
    2019-12-30       False         True
    2019-12-31       False         True
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
        for each stock. The first `length` stocks will be NaN.

    Examples
    --------
    >>>df
                 SPY_Highs  AAPL_Highs  ...  SPY_Closes  AAPL_Closes
    2019-12-02  313.120544  313.120544  ...  310.115326   263.534546
    2019-12-03  308.125122  308.125122  ...  308.035522   258.835724
    2019-12-04  310.592957  310.592957  ...  309.936188   261.120270
    2019-12-05  310.722321  310.722321  ...  310.493439   264.951172
    2019-12-06  313.767365  313.767365  ...  313.329498   270.069031
    2019-12-09  313.637970  313.637970  ...  312.344360   266.288025
    2019-12-10  313.011047  313.011047  ...  311.996063   267.844330
    2019-12-11  313.160339  313.160339  ...  312.881714   270.128906
    2019-12-12  316.434235  316.434235  ...  315.578461   270.817261
    2019-12-13  317.110931  317.110931  ...  315.767517   274.498535
    2019-12-16  318.583679  318.583679  ...  317.936859   279.197357
    2019-12-17  318.683197  318.683197  ...  318.006531   279.746094
    2019-12-18  318.683197  318.683197  ...  318.026398   279.077667
    2019-12-19  319.409637  319.409637  ...  319.329987   279.356995
    2019-12-20  321.974213  321.974213  ...  320.730011   278.778381
    2019-12-23  321.649994  321.649994  ...  321.220001   283.327576
    2019-12-24  321.519989  321.519989  ...  321.230011   283.596924
    2019-12-26  322.950012  322.950012  ...  322.940002   289.223602
    2019-12-27  323.799988  323.799988  ...  322.859985   289.113831
    2019-12-30  323.100006  323.100006  ...  321.079987   290.829773
    2019-12-31  322.130005  322.130005  ...  321.859985   292.954712

    The two missing columns are the Lows of the stocks.

    >>>Not completed yet.

    '''
    True_Ranges = TrueRange(Highs, Lows, Closes)
    if method == 'simple':
        Avg_True_Ranges = True_Ranges.rolling(length).mean()
    elif method == 'wilders':
        Avg_True_Ranges = True_Ranges.ewm(alpha=1/length, min_periods=length).mean()
    return Avg_True_Ranges
