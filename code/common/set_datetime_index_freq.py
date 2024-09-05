# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 10:39:40 2024

@author: ferrucci
"""
#%% Imports
import pandas as pd


#%% Function to check if index is equally spaced

def is_equally_spaced(df):
    """
    Check if a pandas DataFrame index of type DatetimeIndex is equally spaced.
    
    Parameters:
    - df: pandas DataFrame with a DatetimeIndex
    
    Returns:
    - bool: True if the DatetimeIndex is equally spaced, False otherwise
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("The DataFrame index is not a DatetimeIndex.")
    
    differences = df.index.to_series().diff().dropna()
    return differences.nunique() == 1


#%% Set datetime index 'freq' parameter

def set_datetime_index_freq(df):
    """
    Set the 'freq' parameter of a pandas DataFrame index of type DatetimeIndex.
    
    Parameters:
    - df: pandas DataFrame with a DatetimeIndex
    
    Returns:
    - df: pandas DataFrame with the 'freq' parameter set in the DatetimeIndex
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("The DataFrame index is not a DatetimeIndex.")
    
    differences = df.index.to_series().diff().dropna()
    if differences.nunique() != 1:
        raise ValueError("The DatetimeIndex is not equally spaced.")
    
    # Get the unique difference (there should be only one)
    freq = differences.iloc[0]
    
    # Set the freq attribute of the DatetimeIndex
    df.index.freq = pd.to_timedelta(freq)
    
    return df

#%%