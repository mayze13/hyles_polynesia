# -*- coding: utf-8 -*-
"""
Created on Fri May 17 15:31:19 2024

@author: ferrucci
"""


#%% Imports
import pandas as pd
import holidays
# import numpy as np
import warnings

#%%

def h2_load_generator_from_Excel(filename, snapshot_times):

    # Prevent from warning to show
    # Warning: "Data Validation extension is not supported and will be removed"
    warnings.simplefilter(action='ignore', category=UserWarning)
    
    # Import into DataFrame
    df = pd.read_excel(filename,
                       sheet_name='H2 load',
                       header=0,
                       usecols = 'A:E',
                       index_col=[0])
    
    # Remove columns that have all NaN:
    df = df.dropna(axis=1, how='all')
    
    
    # Create empty dataframe
    df_out = pd.DataFrame(index=snapshot_times,
                          columns = df.index.unique().to_list(),
                          data=0.0)

    # Iteratively fill 'df_out' with the infomation from 'df':
    for index, row in df.iterrows():
        # Create temporal df filled with zeros:
        df_temp = pd.Series(index=snapshot_times,
                            data=0.0)

        # Extract values from current row:
        time_start = pd.to_timedelta(row['FROM (≥) (hh:mm)']+':00')
        time_end = pd.to_timedelta(row['TO (<) (hh:mm)']+':00')
        day_type = row['DAY TYPE (Mon/Tue/Wed/Thu/Fri/Sat/Sun/Wk/SS/Hol)']
        power = row['POWER (MW)']
        
        # Parse 'day type' information:
        days = set()
        if day_type == 'Mon':
            days.add(0)
        if day_type == 'Tue':
            days.add(1)
        if day_type == 'Wed':
            days.add(2)
        if day_type == 'Thu':
            days.add(3)
        if day_type == 'Fri':
            days.add(4)
        if day_type == 'Sat':
            days.add(5)
        if day_type == 'Sun':
            days.add(6)
        if day_type == 'Wk':
            days.add(0)
            days.add(1)
            days.add(2)
            days.add(3)
            days.add(4)
        if day_type == 'SS':
            days.add(5)
            days.add(6)
        if day_type == 'Hol':
            pass # See below
            
        # Convert from set to list:
        days_list = list(days)

        # Filter 'snapshot_times' by 'date':
        if day_type == 'Hol':
            fr_holidays = holidays.FRA() # France holidays !
            idx_date = df_temp.index.map(lambda d: d in fr_holidays)
        else:
            idx_date = df_temp.index.day_of_week.isin(days_list)
            
        # Filer 'snapshot_times' by 'time_start' and 'time_end':
        df_index = df_temp.index - df_temp.index.normalize()
        idx_hour = (df_index >= time_start) & (df_index < time_end)
            
        # Applies power set point to the corresponding indexes:
        df_temp.loc[(idx_date & idx_hour)] = power
        
        # Add series to general dataframe:
        df_out.loc[:,index] = df_out.loc[:,index] + df_temp

    
    # Create a series containing the day of the week:    
    df_day_name = pd.Series(index=df_out.index, 
                            name='Day name',
                            data=df_out.index.day_name())

    df_out = pd.concat([df_day_name, df_out],axis=1)
    
    
    return df_out