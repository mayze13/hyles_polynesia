# -*- coding: utf-8 -*-
"""
Created on Thu Aug 25 11:15:51 2022

@author: ferrucci
"""

#%% Imports
import pandas as pd
import numpy as np
import warnings

#%% OK for pypsa 0.28.0
def read_BUS(filename):
    
    # Prevent from warning to show
    # Warning: "Data Validation extension is not supported and will be removed"
    warnings.simplefilter(action='ignore', category=UserWarning)
    
    # Import into DataFrame
    df = pd.read_excel(filename, sheet_name='BUS',
                       header=0,
                       skiprows = [1,2,3,4],
                       usecols = 'B:K',
                       index_col=[0])
    
    # Remove columns that have all NaN:
    df = df.dropna(axis=1, how='all')
    
    return df

#%%  OK for pypsa 0.28.0
def read_LINETYPE(filename):

    # Prevent from warning to show
    # Warning: "Data Validation extension is not supported and will be removed"
    warnings.simplefilter(action='ignore', category=UserWarning)
    
    # Import into DataFrame
    df = pd.read_excel(filename, sheet_name='LINE TYPE',
                       header=0,
                       skiprows = [1,2,3,4],
                       usecols = 'B:J',
                       index_col=[0])
    
    # Remove columns that have all NaN:
    df = df.dropna(axis=1, how='all')
    
    return df

#%% OK for pypsa 0.28.0
def read_LINE(filename):

    # Prevent from warning to show
    # Warning: "Data Validation extension is not supported and will be removed"
    warnings.simplefilter(action='ignore', category=UserWarning)
    
    # Import into DataFrame
    df = pd.read_excel(filename, sheet_name='LINE',
                       header=0,
                       skiprows = [1,2,3,4],
                       usecols = 'B:X',
                       index_col=[0])
    
    # Remove columns that have all NaN:
    df = df.dropna(axis=1, how='all')
    
    return df

#%% OK for pypsa 0.28.0
def read_GENERATOR(filename):

    # Prevent from warning to show
    # Warning: "Data Validation extension is not supported and will be removed"
    warnings.simplefilter(action='ignore', category=UserWarning)
    
    # Import into DataFrame
    df = pd.read_excel(filename, sheet_name='GEN',
                       header=0,
                       skiprows = [1,2,3,4],
                       usecols = 'B:AF',
                       index_col=[0])
    
    # Remove columns that have all NaN:
    df = df.dropna(axis=1, how='all')    
    
    return df

#%% OK for pypsa 0.28.0
def read_TRANSFTYPE(filename):

    # Prevent from warning to show
    # Warning: "Data Validation extension is not supported and will be removed"
    warnings.simplefilter(action='ignore', category=UserWarning)
    
    # Import into DataFrame
    df = pd.read_excel(filename, sheet_name='TRANSF. TYPE',
                       header=0,
                       skiprows = [1,2,3,4],
                       usecols = 'B:Q',
                       index_col=[0])
    
    # Remove columns that have all NaN:
    df = df.dropna(axis=1, how='all')
    
    return df

#%% OK for pypsa 0.28.0
def read_TRANSF(filename):

    # Prevent from warning to show
    # Warning: "Data Validation extension is not supported and will be removed"
    warnings.simplefilter(action='ignore', category=UserWarning)
    
    # Import into DataFrame
    df = pd.read_excel(filename, sheet_name='TRANSF.',
                       header=0,
                       skiprows = [1,2,3,4],
                       usecols = 'B:Z',
                       index_col=[0])
    
    # Remove columns that have all NaN:
    df = df.dropna(axis=1, how='all')
    
    return df

#%% OK for pypsa 0.28.0
def read_LOAD(filename):

    # Prevent from warning to show
    # Warning: "Data Validation extension is not supported and will be removed"
    warnings.simplefilter(action='ignore', category=UserWarning)
    
    # Import into DataFrame
    df = pd.read_excel(filename, sheet_name='LOAD',
                       header=0,
                       skiprows = [1,2,3,4],
                       usecols = 'B:H',
                       index_col=[0])
    
    # Remove columns that have all NaN:
    df = df.dropna(axis=1, how='all')
    
    return df

#%% OK for pypsa 0.28.0
def read_STORAGE_UNIT(filename):

    # Prevent from warning to show
    # Warning: "Data Validation extension is not supported and will be removed"
    warnings.simplefilter(action='ignore', category=UserWarning)
    
    # Import into DataFrame
    df = pd.read_excel(filename, sheet_name='STORAGE UNIT',
                       header=0,
                       skiprows = [1,2,3,4],
                       usecols = 'B:AE',
                       index_col=[0])
    
    # Remove columns that have all NaN:
    df = df.dropna(axis=1, how='all')
    
    return df

#%% OK for pypsa 0.28.0
def read_STORE(filename):

    # Prevent from warning to show
    # Warning: "Data Validation extension is not supported and will be removed"
    warnings.simplefilter(action='ignore', category=UserWarning)
    
    # Import into DataFrame
    df = pd.read_excel(filename, sheet_name='STORE',
                       header=0,
                       skiprows = [1,2,3,4],
                       usecols = 'B:Y',
                       index_col=[0])
    
    # Remove columns that have all NaN:
    df = df.dropna(axis=1, how='all')
    
    return df

#%% OK for pypsa 0.28.0
def read_LINK(filename):

    # Prevent from warning to show
    # Warning: "Data Validation extension is not supported and will be removed"
    warnings.simplefilter(action='ignore', category=UserWarning)
    
    # Import into DataFrame
    df = pd.read_excel(filename, sheet_name='LINK',
                       header=0,
                       skiprows = [1,2,3,4],
                       usecols = 'B:AH',
                       index_col=[0])
    
    # Remove columns that have all NaN:
    df = df.dropna(axis=1, how='all')
    
    return df

#%%
def read_snapshot_names(filename):
    
    # Read first sheet:
    df1 = pd.read_excel(filename, 
                       sheet_name='LOAD SNAPSHOTS',
                       header=None,
                       nrows=1)
    
    # Read second sheet:
    df2 = pd.read_excel(filename, 
                       sheet_name='GEN SNAPSHOTS',
                       header=None,
                       nrows=1)
    
    # Remove first two columns: 
    df1 = df1.drop([0, 1],axis=1)
    df2 = df2.drop([0, 1],axis=1)
    
    # Convert to numpy array in oder to get uniques and compare them:
    np1 = np.unique(np.array(df1))
    np2 = np.unique(np.array(df2))
    
    # Verify that they all have the same snapshot names:
    if not np.array_equal(np1,np2):
        raise Exception('The snapshots'' names are not identical in all the sheets.') 
    
    # Convert to numpy array in order to get unique names:
    return np1.tolist()

#%% 
def read_snapshot_LOAD(filename):
    df = pd.read_excel(filename, 
                       sheet_name='LOAD SNAPSHOTS',
                       header=[0,1],
                       index_col=[0])
    
    # Remove last row, with the SUM of values:
    df = df.drop('SUM',axis=0)
    
    return df
    
#%% 
def read_snapshot_GENERATOR(filename):
    df = pd.read_excel(filename, 
                       sheet_name='GEN SNAPSHOTS',
                       header=[0,1],
                       index_col=[0])
    
    # Remove last row, with the SUM of values:
    df = df.drop('SUM',axis=0)
    
    return df

#%% 
def read_postes_source_xlsx(filename):
    df = pd.read_excel(filename, 
                       header=[0],
                       index_col=[0])
    
    return df

#%% 

    
#%% Test
# filename = '../../data/xlsx/pypsa_rangiroa.xlsx'
# df_lines = read_LINE(filename)
# df_buses = read_BUS(filename)