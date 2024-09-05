# -*- coding: utf-8 -*-
"""
To see this function in action, see script 'swac_TEP_analysis.py'.


Created on Thu Jun 27 14:12:22 2024
@author: ferrucci
"""

#%% Imports
import pandas as pd

#%% Old implementation (day types : Weekdays and Weekends)

def get_daily_profile_old(df, filter_by_type_of_day=False, filter_by_month=False):
    
    #% Remove entire days if there are NaN

    # Create the mask of days where there is at least one NaN:
    df_nan = df.isna().any(axis=1)
    df_nan.name = 'Is NaN'        
    mask_NaN = df_nan.groupby(df_nan.index.normalize()).transform('any')
    mask_NaN.name = 'Mask'
    
    # Apply the mask to the dataframe:
    df = df.loc[~mask_NaN,:]

    #% Type of days (for the moment: Weekday and Weekend):
    is_weekday = df.index.day_of_week < 5
    type_of_day = pd.Series(data=is_weekday,index=df.index)
    type_of_day = type_of_day.replace({True:'Weekday',False:'Weekend'})
    type_of_day.name = 'Type of day'
    
    #% Analysis, hourly
   
    # Get a series with the month number (1 to 12):
    months = pd.Series(data=df.index.month,
                       index=df.index,
                       name='Month')
    
    # Get a series with the minute of the day, starting at midnight:
    minutes = pd.Series((df.index - df.index.normalize()).seconds/60, 
                        index=df.index,
                        name='Minute of the day')
    
    # Concatenate df with the minutes of the day and the type of day:
    df = pd.concat([minutes, months, type_of_day, df],axis=1)

    if filter_by_type_of_day == True:
        if filter_by_month == True:
            # Grouper, group by: 
            #  1. The minute of the day.
            #  2. The month number (1..12).
            #  3. The type of day.
            grouper = df.groupby(['Minute of the day',
                                  'Month',
                                  'Type of day'])
        else:
            # Grouper, group by: 
            #  1. The minute of the day.
            #  2. The type of day.
            grouper = df.drop(columns='Month').groupby(['Minute of the day',
                                                        'Type of day'])
    else:
        if filter_by_month == True:
            grouper = df.drop(columns='Type of day').groupby(['Minute of the day',
                                                              'Month'])
        else:
            # Grouper, group by: 
            #  1. The minute of the day.
            grouper = df.drop(columns=['Month','Type of day']).groupby(['Minute of the day'])

    # Create two series with the average and with the standard deviation:
    df_profile_mean = grouper.mean()
    df_profile_std = grouper.std()

    # Creates an index with the minutes of the day:
    t = pd.timedelta_range(start='00:00:00', 
                           end='23:59:59', 
                           freq=df.index[1]-df.index[0], 
                           name='Time of day') # + pd.to_datetime(df.index[0])

    return df_profile_mean, df_profile_std, t


#%% New implementation (day types: Weekdays, Saturdays, Sundays/Holidays)
import holidays

def get_daily_profile(df, filter_by_type_of_day=False, filter_by_month=False):
    
    # Set holidays
    holidays_polynesia = holidays.country_holidays('FR', subdiv='Polynésie Française')
    
    # Remove entire days if there are NaN

    # Create the mask of days where there is at least one NaN:
    df_nan = df.isna().any(axis=1)
    df_nan.name = 'Is NaN'        
    mask_NaN = df_nan.groupby(df_nan.index.normalize()).transform('any')
    mask_NaN.name = 'Mask'
    
    # Apply the mask to the dataframe:
    df = df.loc[~mask_NaN,:]

    #% Type of days (for the moment: Weekday and Weekend):
    type_of_day = pd.Series(dtype=str,
                            index=df.index,
                            name='Type of day')

    # Assing days of week:
    type_of_day[type_of_day.index.dayofweek < 5]  = 'Weekday'
    type_of_day[type_of_day.index.dayofweek == 5] = 'Saturday'
    type_of_day[type_of_day.index.dayofweek == 6] = 'Sunday/Holiday'

    # Overwrite series with holiday information (brute-force method, there must
    # be something more elegant):
    for i in range(len(type_of_day)):
        if type_of_day.index[i].normalize() in holidays_polynesia:
            type_of_day.iloc[i] = 'Sunday/Holiday'

    #% Analysis, hourly
   
    # Get a series with the month number (1 to 12):
    months = pd.Series(data=df.index.month,
                       index=df.index,
                       name='Month')
    
    # Get a series with the minute of the day, starting at midnight:
    minutes = pd.Series((df.index - df.index.normalize()).seconds/60, 
                        index=df.index,
                        name='Minute of the day')
    
    # Concatenate df with the minutes of the day and the type of day:
    df = pd.concat([minutes, months, type_of_day, df],axis=1)

    if filter_by_type_of_day == True:
        if filter_by_month == True:
            # Grouper, group by: 
            #  1. The minute of the day.
            #  2. The month number (1..12).
            #  3. The type of day.
            grouper = df.groupby(['Minute of the day',
                                  'Month',
                                  'Type of day'])
        else:
            # Grouper, group by: 
            #  1. The minute of the day.
            #  2. The type of day.
            grouper = df.drop(columns='Month').groupby(['Minute of the day',
                                                        'Type of day'])
    else:
        if filter_by_month == True:
            grouper = df.drop(columns='Type of day').groupby(['Minute of the day',
                                                              'Month'])
        else:
            # Grouper, group by: 
            #  1. The minute of the day.
            grouper = df.drop(columns=['Month','Type of day']).groupby(['Minute of the day'])

    # Create two series with the average and with the standard deviation:
    df_profile_mean = grouper.mean()
    df_profile_std = grouper.std()

    # Creates an index with the minutes of the day:
    t = pd.timedelta_range(start='00:00:00', 
                           end  ='23:59:59', 
                           freq=df.index[1]-df.index[0], 
                           name='Time of day') # + pd.to_datetime(df.index[0])

    return df_profile_mean, df_profile_std, t

#%% Extract parameters
from scipy.signal import argrelextrema
import numpy as np

def extract_characteristic_points(time_series, 
                   window_size=5, 
                   first_rel_max_index_min=0, first_rel_max_index_max=None,
                   next_rel_min_index_min=0,  next_rel_min_index_max=None,
                   next_rel_max_index_min=0,  next_rel_max_index_max=None):
    
    # Set default maximum values if not provided
    if first_rel_max_index_max is None:
        first_rel_max_index_max = len(time_series) - 1
    if next_rel_min_index_max is None:
        next_rel_min_index_max = len(time_series) - 1
    if next_rel_max_index_max is None:
        next_rel_max_index_max = len(time_series) - 1

    # Pandas time series
    series = pd.Series(time_series)
    
    # Smooth the time series
    smoothed_series = series.rolling(window=window_size, center=True).mean().bfill().ffill()
    
    # Find the global minimum
    min_index = smoothed_series.idxmin()
    min_value = series.min()
    
    # Find relative maxima and minima
    relative_max_indices = argrelextrema(smoothed_series.values, np.greater, order=2)[0]
    relative_min_indices = argrelextrema(smoothed_series.values, np.less, order=2)[0]

    # Find first relative maxima:
    first_rel_max_index = relative_max_indices[(relative_max_indices >= first_rel_max_index_min) & (relative_max_indices <= first_rel_max_index_max)][0]
    first_rel_max_value = series[first_rel_max_index] if first_rel_max_index is not None else None

    # Find the next relative minimum within the specified range
    next_rel_min_index = relative_min_indices[(relative_min_indices >= next_rel_min_index_min) & (relative_min_indices <= next_rel_min_index_max)][0]
    next_rel_min_value = series[next_rel_min_index] if next_rel_min_index is not None else None
    
    # Find the next relative maximum within the specified range
    next_rel_max_index = relative_max_indices[(relative_max_indices >= next_rel_max_index_min) & (relative_max_indices <= next_rel_max_index_max)][0]
    next_rel_max_value = series[next_rel_max_index] if next_rel_max_index is not None else None
    
    return {
        "min_index": min_index,
        "min_value": min_value,
        "first_rel_max_index": first_rel_max_index,
        "first_rel_max_value": first_rel_max_value,
        "next_rel_min_index": next_rel_min_index,
        "next_rel_min_value": next_rel_min_value,
        "next_rel_max_index": next_rel_max_index,
        "next_rel_max_value": next_rel_max_value
    }


