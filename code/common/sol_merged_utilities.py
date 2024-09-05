# -*- coding: utf-8 -*-
"""
Created on Wed May 22 16:34:30 2024
@author: ferrucci

"""



#%%
import pandas as pd
import numpy as np

def get_PV_timeseries(df_PV_merged, df_PV_meta, times_and_installation, index):
    
    """    
    
    
    Parameters
    ----------
    df_PV_merged : pandas dataframe
        Dataframe from 'sol_merged.pkl' file.
        
    df_PV_meta : pandas dataframe
        Data from 'sol_merged_metadata.pkl'.
        
    times_and_installation : dict
        Dictionary with the following information:
        - a list with the names of the PV installation
        - a list with the start of each time-series
        - a list with the name of the PV installation as found in 'sol_merged.pkl'
        
        Example:
        times_and_installation = {'name':['PV1',
                                          'PV2',], 
                                  'start_time':[pd.to_datetime('12-Sep-2020 00:00:00'),
                                                pd.to_datetime('12-Jul-2019 00:00:00'),],
                                  'installation_name':['sol_2403',
                                                       'sol_0476',]
                                  }

    index : pandas DatetimeIndex object
        Time index of the output dataframe.

    Returns
    -------
    df_out : pandas dataframe
        Dataframe with the PV time-series.

    """    
    
    names = times_and_installation['name']
    start_times = times_and_installation['start_time']
    installation_name = times_and_installation['installation_name']
    
    # Create empty output dataframe:
    df_out = pd.DataFrame(index=index,
                          columns=names,
                          dtype=np.float64)
    
    # Create auxiliar dataframe:
    idx_aux_start = index[0]
    idx_aux_end = index[-1]
    idx_aux_freq = df_PV_merged.index.freq
    idx_aux = pd.date_range(start=idx_aux_start,
                            end=idx_aux_end,
                            freq=idx_aux_freq,
                            inclusive='both')
    
    # Auxiliar dataframe, with the start and end times of 'index', but with the
    # frequency of 'df_PV_merged':
    df_aux = pd.DataFrame(index=idx_aux,
                          columns=times_and_installation['name'],
                          dtype=np.float64)

    # Compute the number of points to extract from each PV installation time-series:
    num_point_to_extract = idx_aux.size           
    
    # Get points and fill df_aux:
    for i in range(len(names)):
        peak_i = df_PV_meta.loc[installation_name[i],'peak_power_kW']

        idx_i = pd.date_range(start=start_times[i],
                              periods=num_point_to_extract,
                              freq=idx_aux_freq,
                              inclusive='left')
        df_aux.iloc[:,i] = df_PV_merged.loc[idx_i, installation_name[i]]/peak_i
       
    # Replace NaN by zeros:
    df_aux[df_aux.isna()] = 0
        
    # Resample 'df_aux' and get 'df_out':
    df_out = df_aux.resample(index.freq).mean()
    
    return df_out