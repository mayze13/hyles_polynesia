# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 19:54:08 2022

@author: ferrucci
"""

#%% Imports
from geopy import distance
import requests
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.io as pio

#%%
def coordinates_to_string(M):
    """
    Convert an array of coordinates into a string to be used with the API
    https://api.open-elevation.com/api/v1/lookup?locations=lat1,long1|lat2,long2|...

    Parameters
    ----------
    M : numpy array. An array of coordinates. 
        The first column is the latitude and the second is the longitude.

    Returns
    -------
    string
        The concatenation of all the rows separated by '|':
            lat1, long1 | lat2, long2 | ...
    """
    num_rows = M.shape[0]
    string = ""
    for row in range(num_rows):
        string += str(M[row,0]) + ',' + str(M[row,1]) + '|'
    
    return string[0:-1]

#%%
def get_elevation(lat, long):
    query = ('https://api.open-elevation.com/api/v1/lookup'
             f'?locations={lat},{long}')
    r = requests.get(query).json()  # json object, various ways you can extract value
    # one approach is to use pandas json functionality:
    elevation = pd.io.json.json_normalize(r, 'results')['elevation'].values[0]
    return elevation

#%%
def get_elevation_multiple(lat_long_matrix, MAX_NUM_COORDINATES_REQUESTS=100):
    """
    Script for returning elevation from lat, long, based on open elevation data
    which in turn is based on SRTM

    Parameters
    ----------
    lat_long_matrix : NUMPY
        Matrix with longitude, latid.

    Returns
    -------
    elevation : TYPE
        DESCRIPTION.

    """

    # Pre-allocation:
    elevation = np.zeros(len(lat_long_matrix))
        
    # Split M into multiple matrices if number of rows 
    # is > MAX_NUM_COORDINATES_REQUESTS (otherwise the requests.get(url) 
    # does not work):
    chunk_size = MAX_NUM_COORDINATES_REQUESTS
    
    lat_long_split = np.array_split(lat_long_matrix,
                                    math.ceil(len(lat_long_matrix)/chunk_size))
    
    elevation_split = np.array_split(elevation,
                                     math.ceil(len(elevation)/chunk_size))
    
    # Iterate over the two chunks at the same time:
    for M, elev in zip(lat_long_split,elevation_split):
        lat_long_str = coordinates_to_string(M)
        query = ('https://api.open-elevation.com/api/v1/lookup'
                  f'?locations={lat_long_str}')
        r = requests.get(query).json()  # json object, various ways you can extract value
        # one approach is to use pandas json functionality:
        elev[::] = pd.io.json.json_normalize(r, 'results')['elevation'].values
    
    # Done!
    return elevation

#%%
def get_flat_distance_meter(p1, p2):
    flat_distance = distance.distance(p1[0:2], p2[0:2]).m
    return flat_distance

#%%
def get_euclidian_distances_meter(lat_long_elev_matrix):
    
    # Number of coordinates points:
    num = lat_long_elev_matrix.shape[0]
    
    # Pre-allocation:
    distances = np.zeros((num-1))
    
    # Loop:
    for i in range(num-1):
        # Get flat distance:
        flat_distance_i = get_flat_distance_meter(lat_long_elev_matrix[i, 0:2],
                                                  lat_long_elev_matrix[i+1, 0:2])
        # Get euclidian distance:
        dist_i = math.sqrt(flat_distance_i**2 + (lat_long_elev_matrix[i,2] - lat_long_elev_matrix[i+1,2])**2)
        
        # Assing to vector:
        distances[i] = dist_i
        
    return distances

#%%
def uniqueish_color():
    """There're better ways to generate unique colors, but this isn't awful."""
    return plt.cm.gist_ncar(np.random.random())

#%%

def get_buses_coordinates(excel_path):
    """
    Reads the file 'pypsa_tahiti.xlsx' and return a dataframe with the list
    of buses and their coordinates

    Parameters
    ----------
    excel_path : str
        The path of the Excel file.

    Returns
    -------
    df : dataframe
        The table with the list of buses and their coordinates x (longitude)
        and y (latitude)
    """
    df = pd.read_excel(excel_path,header=0, 
                       usecols=['name','x','y'], 
                       skiprows=[1,2,3,4],
                       index_col=0,
                       dtype={'name':str,'x':np.float64,'y':np.float64},
                       sheet_name='BUS')
    return df

# file_path = './data/pypsa_tahiti.xlsx'
# df = get_buses_coordinates(file_path)

#%% Plot function using Plotly
def plot(df,vars_to_plot, title, show=True):
    pio.renderers.default='browser' # plot into web browser
    
    fig = px.line(data_frame=df, x=df.index, y=vars_to_plot,
                    title=title,
                    labels={"x": "Time",
                            "value": "Various units",
                            "variable": "List of variables"})
    if show == True:
        fig.show() 
        
    return fig