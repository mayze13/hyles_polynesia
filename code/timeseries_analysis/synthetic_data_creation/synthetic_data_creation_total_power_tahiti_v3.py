# -*- coding: utf-8 -*-
"""
TAHITI HOURLY SYNTHETIC TOTAL POWER PROFILE.

NOTE JUNE 2024: many of the code from part A has been ported to 
    'code\timeseries_analysis\tahiti\import_edt\edt_power_profile_analysis.py'



The code can be divided into two parts:
    a. Getting the statistical properties of the real power profile from imported data.
    b. Use of these statistical properties to synthetize a new power profile.
    
A. GETTING THE STATISTICAL PROPERTIES OF THE REAL POWER PROFILE
   The steps are the following:
        1. It reads the Tahiti's power profile data from 2015 to 2020 
           (source: SDE), which has a time step of 10 minutes. 
        
        2. It resamples the data in order to get an hourly profile.
        
        3. It groupes the time series values into :
            a. Month number (1..12)
            b. Hour of the day (0..23)
            c. Type of day (Weekday, Saturday and Sunday/Holiday)
        
        4. For each group of data (Month, Hour of day, Type of day), it computes 
           its statistical properties (mean, standard deviation, etc). 
           These statistical properties are found 'df_stats' dataframe.
           
B. USE OF THESE STATISTICAL PROPERTIES TO SYNTHETIZE A POWER PROFILE
   The steps are the following:
        1. Create a dataframe with the power equal to the mean value at each 
           corresponding time stamp ('df_synthetic_mean').
           The mean value is a function of the month, hour of the day and type of day 
           (weekday, Saturday or Sunday/Holiday).
           
           This means that, for instance, the power at time 10AM of all work days
           of the month of July will have the same power.
           
        2. Scale the time-series so that the total energy is equal to the target 
           total energy ('GWh_year_target' variable).
        3. Add randomness at each time stamp and obtain final dataframe ('df_synthetic')
        
        4. Final resample to remove fast changing behaviour.
        
        Note: the scale is applied before applying the randomness. This is done to
        preserve the standard deviation of each sample power (as it is assumed, by
        hypothesis, that the standard deviation doesn't scale)


Notes:
    
    1. The histogram shows that, for a particular day of the year and hour of 
       the day, the distribution is not necessarily gaussian.
       The histrogram could then be used as a probability density function to 
       generate the randomness (instead of adding a zero-mean randon number 
       with a standard deviation equal to the sampled std).
       A word of warning: for the 'Weekdays', the histrogram is sufficiently 
       rich (more than 100 counts). However, this is not the case for Saturday
       and Sunday/Holiday, in which cases the histogram is less representative.
        
    2. Year 2020 was COVID year, so maybe we should take it out of the initial
       power profile.    

    3. The library 'holydays' does not always return the good values of holidays
       for French Polynesia.

To do:
    
    1. Add day-to-day variability of the dayly profile (as in HOMER Pro)

Created on Sat Sep 24 21:13:03 2022
@author: Franco Ferrucci
"""

#%% Setting path
import sys
sys.path.append('../../common')

#%% Imports
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

import matplotlib.pyplot as plt
import plotly.io as pio
import utils

from get_daily_profile import extract_characteristic_points

#%% Set plotly to plot in browser
pio.renderers.default='browser'

#%% Load data SDE
path2 = r"./../../../data/pkl/EDT_Tahiti_2015_2022.pkl"
df_SDE = pd.read_pickle(path2)

#%% Load holidays file
path3 = r'./data/holidays_Polynesia_2015_2022.pkl'
holidays_Polynesia_2015_2022 = pd.read_pickle(path3)

#%% Get holidays from library
# Warning: sometimes the library gives wrong results  !!!!

import holidays
holidays_polynesia = holidays.country_holidays('FR', subdiv='Polynésie Française')

#%% Load day-to-day variability distribution
path4 = r'./data/day_to_day_variability_ecdf.pkl'
df_day_to_day_variability_ecdf = pd.read_pickle(path4)

#%% Get data as a pandas Series
data = df_SDE['total_MW']
data.name = 'Total power (MW)'

#%% Resample and filter for a particular year

# Choose if only one year will be analyzed:
one_year_only = False

if one_year_only == True:
    year_to_analyse = 2019
    mask_data = data.index.year == year_to_analyse
    data_resampled = data[mask_data].resample('10 min').mean()
else:
    data_resampled = data.resample('10 min').mean()


# Number of point per day of the power profile time-series:
num_points_per_day = len((data_resampled.index - data_resampled.index.normalize()).unique())

# Time step, in hours:
dT_hour = 24/num_points_per_day

#%%
plot_this_plot = True

if plot_this_plot:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data_resampled.index,
                             y=data_resampled,
                             mode='lines',
                             name= 'Total power (MW)'))
    
    
    fig.update_layout(title='Tahti power production - Real data')
    fig.show()

#%% Create dataframe with information of type of day (Weekday, Saturday, Sunday/Holiday)

# from pandas.api.types import CategoricalDtype
# cat_type = CategoricalDtype(categories=['Weekday', 'Saturday', 'Sunday or Holiday'], ordered=True)
# type_of_day_categories = np.array(['Weekday', 'Saturday', 'Sunday/Holiday'])

type_of_day = pd.Series(dtype=str,
                        index=data_resampled.index,
                        name='Type of day')

# Assing days of week:
type_of_day[type_of_day.index.dayofweek < 5] = 'Weekday'
type_of_day[type_of_day.index.dayofweek == 5] = 'Saturday'
type_of_day[type_of_day.index.dayofweek == 6] = 'Sunday/Holiday'

# Overwrite series with holiday information (brute-force method, there must
# be something more elegant):
for i in range(len(type_of_day)):
    if type_of_day.index[i].normalize() in holidays_Polynesia_2015_2022.index:
        type_of_day.iloc[i] = 'Sunday/Holiday'

# type_of_day = type_of_day.astype('category')

# Concatenate:
df = pd.concat([type_of_day, data_resampled],axis=1)

#%% Compare holidays libraries

# type_of_day2 = type_of_day.copy()

# # Assing days of week:
# type_of_day2[type_of_day2.index.dayofweek < 5] = 'Weekday'
# type_of_day2[type_of_day2.index.dayofweek == 5] = 'Saturday'
# type_of_day2[type_of_day2.index.dayofweek == 6] = 'Sunday/Holiday'

# # Overwrite series with holiday information (brute-force method, there must
# # be something more elegant):
# for i in range(len(type_of_day2)):
#     if type_of_day2.index[i].normalize() in holidays_polynesia:
#         type_of_day2.iloc[i] = 'Sunday/Holiday'
    
# # Compare:
# mask1 =  type_of_day.index.normalize() == type_of_day.index
# mask2 =  type_of_day2.index.normalize() == type_of_day2.index
# x = type_of_day[mask1].compare(type_of_day2[mask2])

# df_compare_holidays = pd.concat([type_of_day, type_of_day2],axis=1)
# df_compare_holidays.columns = ['Mine','From library']

# mask3 = df_compare_holidays.index.normalize() == df_compare_holidays.index
# df_compare_holidays = df_compare_holidays.loc[mask3,:]

#%% Compute stats ('df_stats' dataframe)

# Grouper index, month number:   
grouper1_idx1 = df.index.month   # Month (1, 2, ..., 12)

# Grouper index, minute of the day:
grouper1_idx2 = (df.index - df.index.normalize()).seconds/60
    
grouper1 = df.groupby([grouper1_idx1,  # month number (1..12)
                       grouper1_idx2,  # minute of the day (0..1440)
                       'Type of day'])  

# Compute stats:
df_stats = grouper1.agg([np.mean, np.std, np.median, np.max, np.min, np.count_nonzero])

# Rename indexes:
df_stats.index = df_stats.index.set_names('Month', level=0)
df_stats.index = df_stats.index.set_names('Time of day', level=1)

# Remove MultiIndex in column
df_stats.columns = df_stats.columns.droplevel(0)

#%% Plot mean with std
import calendar
month_list = list(calendar.month_abbr[1:])

plot_this_plot = True

if plot_this_plot:
    fig1 = go.Figure()
    for month_number in range(1,len(month_list)+1):
        for this_type in df_stats.index.get_level_values('Type of day').unique():
            fig1.add_trace(go.Scatter(x=grouper1_idx2.unique(),
                                     y=df_stats.loc[(month_number,slice(None),this_type),'mean'],
                                     error_y=dict(
                                           type='data', # value of error bar given in data coordinates
                                           array=df_stats.loc[(month_number,slice(None),this_type),'std'].values,
                                           visible=True),
                                     mode='lines+markers',
                                     name= month_list[month_number-1] +' ,'+ this_type))
    
    fig1.show()

#%%
# Initialize dataframe:
col0 = ['Weekday','Sunday/Holiday','Saturday']
col1 = ['min_index',
       'min_value',
       'first_rel_max_index',
       'first_rel_max_value',
       'next_rel_min_index',
       'next_rel_min_value',
       'next_rel_max_index',
       'next_rel_max_value',
      ]
idx = np.arange(1,13) # month number
df_stats_parameters = pd.DataFrame(data=0.0,
                                   index=idx, 
                                   columns=pd.MultiIndex.from_product([col0, col1]),
                                   )
# Rename indexes:
df_stats_parameters.index = df_stats_parameters.index.set_names('Month')
df_stats_parameters.columns = df_stats_parameters.columns.set_names('Type of day', level=0)
df_stats_parameters.columns = df_stats_parameters.columns.set_names('Parameter', level=1)

# Define type:
df_stats_parameters.loc[:,(slice(None),'min_index')] = df_stats_parameters.loc[:,(slice(None),'min_index')].astype('int64')
df_stats_parameters.loc[:,(slice(None),'min_value')] = df_stats_parameters.loc[:,(slice(None),'min_value')].astype('float64')
df_stats_parameters.loc[:,(slice(None),'first_rel_max_index')] = df_stats_parameters.loc[:,(slice(None),'first_rel_max_index')].astype('int64')
df_stats_parameters.loc[:,(slice(None),'first_rel_max_value')] = df_stats_parameters.loc[:,(slice(None),'first_rel_max_value')].astype('float64')
df_stats_parameters.loc[:,(slice(None),'next_rel_min_index')] = df_stats_parameters.loc[:,(slice(None),'next_rel_min_index')].astype('int64')
df_stats_parameters.loc[:,(slice(None),'next_rel_min_value')] = df_stats_parameters.loc[:,(slice(None),'next_rel_min_value')].astype('float64')
df_stats_parameters.loc[:,(slice(None),'next_rel_max_index')] = df_stats_parameters.loc[:,(slice(None),'next_rel_max_index')].astype('int64')
df_stats_parameters.loc[:,(slice(None),'next_rel_max_value')] = df_stats_parameters.loc[:,(slice(None),'next_rel_max_value')].astype('float64')

# Iterate over df_stats and fill dataframe:
for month_number in df_stats_parameters.index.values:
    for this_type in df_stats.index.get_level_values('Type of day').unique():
        data = df_stats.loc[(month_number,slice(None),this_type),'mean'].values
        param = extract_characteristic_points(data,
            first_rel_max_index_min=40, first_rel_max_index_max=100,
            next_rel_min_index_min=90, next_rel_min_index_max=112,
            next_rel_max_index_min=100, next_rel_max_index_max=140,)
        df_stats_parameters.loc[month_number,(this_type,'min_index')] = param['min_index']
        df_stats_parameters.loc[month_number,(this_type,'min_value')] = param['min_value']
        df_stats_parameters.loc[month_number,(this_type,'first_rel_max_index')] = param['first_rel_max_index']
        df_stats_parameters.loc[month_number,(this_type,'first_rel_max_value')] = param['first_rel_max_value']
        df_stats_parameters.loc[month_number,(this_type,'next_rel_min_index')] = param['next_rel_min_index']
        df_stats_parameters.loc[month_number,(this_type,'next_rel_min_value')] = param['next_rel_min_value']
        df_stats_parameters.loc[month_number,(this_type,'next_rel_max_index')] = param['next_rel_max_index']
        df_stats_parameters.loc[month_number,(this_type,'next_rel_max_value')] = param['next_rel_max_value']
        
# print(df_stats_parameters.dtypes)
del(data, param, month_number, this_type)

#%% Same as 'df_stats_parameters', but with indexes in pd.Timedelta format

dT = pd.Timedelta(data_resampled.index.freq)

df_stats_parameters2 = df_stats_parameters.copy()
for this_type in df_stats.index.get_level_values('Type of day').unique():
    # Change type
    df_stats_parameters2[(this_type,'min_index')] = \
        df_stats_parameters2[(this_type,'min_index')].astype('timedelta64[ns]')
    # Now perform the assignment
    df_stats_parameters2.loc[:, (this_type, 'min_index')] = \
        pd.to_timedelta(df_stats_parameters.loc[:,(this_type,'min_index')] * dT.seconds, 's') \
            .astype('timedelta64[ns]')

    # Change type
    df_stats_parameters2[(this_type,'first_rel_max_index')] = \
        df_stats_parameters2[(this_type,'first_rel_max_index')].astype('timedelta64[ns]')
    # Now perform the assignment
    df_stats_parameters2.loc[:, (this_type, 'first_rel_max_index')] = \
        pd.to_timedelta(df_stats_parameters.loc[:,(this_type,'first_rel_max_index')] * dT.seconds, 's') \
            .astype('timedelta64[ns]')

    # Change type
    df_stats_parameters2[(this_type,'next_rel_min_index')] = \
        df_stats_parameters2[(this_type,'next_rel_min_index')].astype('timedelta64[ns]')
    # Now perform the assignment
    df_stats_parameters2.loc[:, (this_type, 'next_rel_min_index')] = \
        pd.to_timedelta(df_stats_parameters.loc[:,(this_type,'next_rel_min_index')] * dT.seconds, 's') \
            .astype('timedelta64[ns]')

    # Change type
    df_stats_parameters2[(this_type,'next_rel_max_index')] = \
        df_stats_parameters2[(this_type,'next_rel_max_index')].astype('timedelta64[ns]')
    # Now perform the assignment
    df_stats_parameters2.loc[:, (this_type, 'next_rel_max_index')] = \
        pd.to_timedelta(df_stats_parameters.loc[:,(this_type,'next_rel_max_index')] * dT.seconds, 's') \
            .astype('timedelta64[ns]')

#%% Save dataframe to pickle file
# df_stats_parameters2.to_pickle(r"./../../../data/pkl/EDT_Tahiti_2015_2022_power_profile_parameters.pkl")

#%% Plot power profile and identified parameters
plot_this_plot = True
        
if plot_this_plot:        
    fig2 = go.Figure()
    for month_number in df_stats_parameters.index.values:
        for this_type in df_stats.index.get_level_values('Type of day').unique():
            data = df_stats.loc[(month_number,slice(None),this_type),'mean'].values
            # Plot profile:
            fig2.add_trace(go.Scatter(x=np.arange(len(data)),
                                      y=data))
            # Organize parameters for easy plotting:
            idx = [
                df_stats_parameters.loc[month_number,(this_type,'min_index')],
                df_stats_parameters.loc[month_number,(this_type,'first_rel_max_index')],
                df_stats_parameters.loc[month_number,(this_type,'next_rel_min_index')],
                df_stats_parameters.loc[month_number,(this_type,'next_rel_max_index')],
                  ]
                  
            points = [
                df_stats_parameters.loc[month_number,(this_type,'min_value')],
                df_stats_parameters.loc[month_number,(this_type,'first_rel_max_value')],
                df_stats_parameters.loc[month_number,(this_type,'next_rel_min_value')],
                df_stats_parameters.loc[month_number,(this_type,'next_rel_max_value')],
            ]    
            # Plot parameters:
            fig2.add_trace(go.Scatter(x=idx,
                                      y=points,
                                      mode='markers',
                                      marker=dict(symbol='diamond', size=12),
                                      ))
    fig2.show()        

#%% Plot identified parameter over time
plot_this_plot = True
        
if plot_this_plot:
    fig3 = go.Figure()
    for this_type in df_stats.index.get_level_values('Type of day').unique():
        fig3.add_trace(go.Scatter(x=df_stats_parameters.index,
                                  y=df_stats_parameters.loc[:,(this_type,'min_index')] * pd.Timedelta(data_resampled.index.freq).seconds/3600,
                                  name='min_index '+this_type))
    for this_type in df_stats.index.get_level_values('Type of day').unique():
        fig3.add_trace(go.Scatter(x=df_stats_parameters.index,
                                  y=df_stats_parameters.loc[:,(this_type,'first_rel_max_index')] * pd.Timedelta(data_resampled.index.freq).seconds/3600,
                                  name='first_rel_max_index '+this_type))
    for this_type in df_stats.index.get_level_values('Type of day').unique():
        fig3.add_trace(go.Scatter(x=df_stats_parameters.index,
                                  y=df_stats_parameters.loc[:,(this_type,'next_rel_min_index')] * pd.Timedelta(data_resampled.index.freq).seconds/3600,
                                  name='next_rel_min_index '+this_type))
    for this_type in df_stats.index.get_level_values('Type of day').unique():
        fig3.add_trace(go.Scatter(x=df_stats_parameters.index,
                                  y=df_stats_parameters.loc[:,(this_type,'next_rel_max_index')] * pd.Timedelta(data_resampled.index.freq).seconds/3600,
                                  name='next_rel_max_index '+this_type))
    fig3.show()

#%% View histogram of a selected hour of the year:

plot_this_plot = True

if plot_this_plot:   
    # Select month, hour and type of day:
    hist_month = 8
    hist_time_of_day = 3.5*60
    hist_type_of_day = 'Saturday'
    
    # Compute histogram:
    hist_data = grouper1.get_group((hist_month,hist_time_of_day,hist_type_of_day))
    
    # Plot:
    fig = px.histogram(hist_data['Total power (MW)'],nbins=40)
    title_str = 'Histrogram of a particular month, time of day and type of day. ' + \
                'Month = {0}, Time = {1} hour, Type of day = {2}' \
                .format(month_list[hist_month],hist_time_of_day/60, hist_type_of_day)
    fig.update_layout(title=title_str)
    fig.show()

#%% Initialize synthetic electricity production series
'''
In this section we create a dataframe named 'df_synthetic_mean' that as an
envelope of the power profile. This envelope depends on the type of day (working
day, Saturday or Sunday/Holiday) and the month.

'''

# Choose year to synthetize:
year_to_synthetize = 2019

# Create time index:
time_idx = pd.date_range(start='01-Jan-' + str(year_to_synthetize), 
                    end='01-Jan-' + str(year_to_synthetize+1),
                    freq='10 min', 
                    inclusive='left',
                    name='Date')

# Create empty dataframe:
df_synthetic_mean = pd.DataFrame(columns=['EV_power_MW'],
                                 index=time_idx)

# Asign month, dya of the month, and hour:
df_synthetic_mean.loc[:,'Month'] = df_synthetic_mean.index.month
df_synthetic_mean.loc[:,'Day of the month'] = df_synthetic_mean.index.day

df_synthetic_mean.loc[:,'Time of day'] = (df_synthetic_mean.index - df_synthetic_mean.index.normalize()).seconds/60

# Assing days of week:
df_synthetic_mean.loc[df_synthetic_mean.index.dayofweek < 5,'Type of day'] = 'Weekday'
df_synthetic_mean.loc[df_synthetic_mean.index.dayofweek == 5,'Type of day'] = 'Saturday'
df_synthetic_mean.loc[df_synthetic_mean.index.dayofweek == 6,'Type of day'] = 'Sunday/Holiday'

# Overwrite series with holiday information (brute-force method, there must
# be something more elegant):
for index, row in df_synthetic_mean.iterrows():
    if index.normalize() in holidays_polynesia:
        df_synthetic_mean.loc[index,'Type of day'] = 'Sunday/Holiday'

# Add 'Day name' (Monday, Tuesday, ..., Sunday, Holiday):
df_synthetic_mean.loc[df_synthetic_mean.index.dayofweek == 0,'Day name'] = 'Monday'
df_synthetic_mean.loc[df_synthetic_mean.index.dayofweek == 1,'Day name'] = 'Tuesday'
df_synthetic_mean.loc[df_synthetic_mean.index.dayofweek == 2,'Day name'] = 'Wednesday'
df_synthetic_mean.loc[df_synthetic_mean.index.dayofweek == 3,'Day name'] = 'Thursday'
df_synthetic_mean.loc[df_synthetic_mean.index.dayofweek == 4,'Day name'] = 'Friday'
df_synthetic_mean.loc[df_synthetic_mean.index.dayofweek == 5,'Day name'] = 'Saturday'
df_synthetic_mean.loc[df_synthetic_mean.index.dayofweek == 6,'Day name'] = 'Sunday'


# Overwrite series with holiday information (brute-force method, there must
# be something more elegant):
for index, row in df_synthetic_mean.iterrows():
    if index.normalize() in holidays_polynesia:
        df_synthetic_mean.loc[index,'Day name'] = 'Holiday'

# Compute mean values for each time stamp of the time-series:
for index, row in df_synthetic_mean.iterrows():
    # For each row, get month, hour and type of day:
    M = row['Month']
    m = row['Time of day']
    t = row['Type of day']
    # Fetch mean:
    mean_i = df_stats.loc[(M,m,t),'mean']
    # Set mean to time-series:
    df_synthetic_mean.loc[index,'Total power (MW)'] = mean_i

#%% Plot 'df_synthetic_mean'
plot_this_plot = True
if plot_this_plot:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_synthetic_mean.index,
                             y=df_synthetic_mean.loc[:,'Total power (MW)'],
                             mode='lines',
                             name= 'Total power (MW) (mean)'))
    
    fig.update_layout(title='Tahti power production - Synthetic data (envelope)')
    
    fig.show()

#%% Add day-to-day variability, initialization
"""
1. Establecer día de referencia (MWh_day fijo)
2. Calculo la energia del día actual ( Ecurrent(before) ) y del día anterior (Eprevious)
3. Calculo Kbefore = Ecurrent(before)/Eprevious
4. Tiro una moneda con una distribución según el día en que encuentre (lunes,
   martes, ..., domingo, feriado). Esta moneda me devuelve Knew
5. Calculo el factor de multiplicación a afectar a Ecurrent para que K sea 
   igual a Knew:
        deltaK = Knew/Kbefore
6. Hago: Ecurrent(new) = Ecurrent(before)*deltaK
   

La referencia podría ser alguno de los casos siguientes (a estudiar):
    - el primer lunes de cada mes
    - cada primero de cada mes
    - cada 8 días (para que la refencia no se repita)
    - ...
No estoy seguro si habría mucha diferencia.

"""

# Initialize a series that indicates if the day is a reference day (so its dayly
# production must not be modified by a day-to-day variability factor):   
is_reference_day = pd.Series(data=False,dtype='bool', index = df_synthetic_mean.index)
is_reference_day.name = 'Is reference day'

# First day of the year must be a reference day (initial condition):
mask_first_day_of_year = is_reference_day.index.day_of_year == 1
is_reference_day[mask_first_day_of_year] = True    

# The days after Holidays must be set as reference days
group_reference_day_2 = is_reference_day.groupby(is_reference_day.index.normalize())

for name_today, group_today in group_reference_day_2:
    # Initialize 'name_yesterday':
    if name_today.day_of_year == 1:
        name_yesterday = name_today 
        continue
    
    if df_synthetic_mean.loc[name_yesterday,'Day name'] == 'Holiday':
        is_reference_day[group_today.index] = True
    
    # Update 'name_yesterday':
    name_yesterday = name_today

#%% Choose which days are marked as reference.
#   Option 1: the 1st working day ('Weekday') of the month:
    
# Create a mask with days of the year marked as 'Weekday':    
mask_weekday = df_synthetic_mean['Type of day'] == 'Weekday'
    
# Get a subset of 'is_reference_day':
is_reference_day_Weekday = is_reference_day[mask_weekday]

# Group accoring to month (1,2,...,12) and day of month (1,..28/29/30/31):
group_reference_day = is_reference_day_Weekday.groupby(
    [is_reference_day_Weekday.index.month,
     is_reference_day_Weekday.index.day])

# Get list of groups:
L1 = list(group_reference_day.groups.keys())

# Convert list of tuples to array:
L2 = np.array(L1)

# Convert to Dataframe:
L3 = pd.DataFrame(L2,columns=['Month','Day'])

# Get first 'Day' of each 'Month':
L4 = L3.groupby('Month',as_index=False).first()

# Convert Dataframe to tuple:
L5 = list(L4.itertuples(index=False, name=None))

# Get groups for each tuple and assing 'Is reference day' to True:
for this_tuple in L5:
    idx = group_reference_day.get_group(this_tuple).index
    is_reference_day[idx] = True

# Done! Now the 'is_reference_day' Series is True on the days we don't want
# to modify the value of daily energy.

# Add 'is_reference_day' Series to 'df_synthetic_mean':
if 'Is reference day' in df_synthetic_mean.columns:
    df_synthetic_mean['Is reference day'] = is_reference_day
else:
    df_synthetic_mean = pd.concat([df_synthetic_mean, 
                                   is_reference_day],axis=1)

#%% Choose which days are marked as reference.
#   Option 2: every 8th day

# Set the step:
reference_day_step = 6

# Create group that go through 'is_reference_day' on a daily basis:
group_reference_day_2 = is_reference_day.groupby(is_reference_day.index.normalize())

for name, group in group_reference_day_2:
    if name.day_of_year % reference_day_step == 0:
        is_reference_day[group.index] = True
        
# Done! Now the 'is_reference_day' Series is True on the days we don't want
# to modify the value of daily energy.

# Add 'is_reference_day' Series to 'df_synthetic_mean':
if 'Is reference day' in df_synthetic_mean.columns:
    df_synthetic_mean['Is reference day'] = is_reference_day
else:
    df_synthetic_mean = pd.concat([df_synthetic_mean, 
                                   is_reference_day],axis=1)

#%% Add day-to-day variability, computation 

# Initialization:
df_synthetic_mean_with_daily_variability = df_synthetic_mean.copy(deep=True)

# Create a group in order to loop in a daily basis:
grouper_daily = df_synthetic_mean_with_daily_variability.groupby(
    df_synthetic_mean_with_daily_variability.index.normalize())

# Get list of groups in 'grouper_daily':
grouper_daily_idx = list(grouper_daily.groups.keys())

for name_today, group_today in grouper_daily:
    
    # Initialize 'name_yesterday':
    if name_today.day_of_year == 1:
        name_yesterday = name_today # this day must also be a reference day!
        continue
    
    # If day is reference day, continue without modifying:
    if group_today['Is reference day'].all() == True:
        print('{0} is a reference day. Skip.'.format(name_today))
        
        # Update 'name_yesterday':
        name_yesterday = name_today
        continue
    
    # Compute current daily energy:
    E_today_before_MWh = group_today['Total power (MW)'].sum() * dT_hour
    
    # Compure previous day daily energy:
    group_yesterday = grouper_daily.get_group(name_yesterday)
    # group_yesterday = df_synthetic_mean_with_daily_variability.loc[group_today.index] # it's the same!
    
    E_yesterday_MWh = group_yesterday['Total power (MW)'].sum() * dT_hour
    
    # Compute variability before appliying randomness:
    Kbefore = E_today_before_MWh/E_yesterday_MWh
    
    # Get random number representing daily variability (Energy today/Energy yesterday):
    ecdf_idx = group_today['Day name'][0]
    ecdf_x = df_day_to_day_variability_ecdf.loc[ecdf_idx,'cdf x']
    ecdf_y = df_day_to_day_variability_ecdf.loc[ecdf_idx,'cdf y']
    
    Knew = 1/(1- utils.get_random_array_from_ecdf(ecdf_x, ecdf_y, 1)[0])
    
    # Compute 
    deltaK = Knew/Kbefore
    
    # Compute new current daily energy:
    E_today_new_MWh = E_today_before_MWh * deltaK
    
    # Apply scale factor to all sample of current day:
    df_synthetic_mean_with_daily_variability.loc[group_today.index,'Total power (MW)'] *= deltaK
    
    # Update 'name_yesterday':
    name_yesterday = name_today
    
    # Print Kbefore and Knew:
    # print('Day name = {}'.format(ecdf_idx))
    # print('Kbefore = {}'.format(Kbefore))
    # print('Knew = {}'.format(Knew))
    
    # DEBUG:
    # if name_today.month == 3:
    #     break
    

# Plot
fig = go.Figure()
# fig.add_trace(go.Scatter(x=df_synthetic_mean.index,
#                          y=df_synthetic_mean.loc[:,'Total power (MW)'],
#                          mode='lines',
#                          name= 'Total power (MW) (mean)'))

fig.add_trace(go.Scatter(x=df_synthetic_mean_with_daily_variability.index,
                         y=df_synthetic_mean_with_daily_variability.loc[:,'Total power (MW)'],
                         mode='lines',
                         name= 'Total power (MW) (with daily variability)'))

# fig.update_layout(title='Tahti power production - Synthetic data (envelope)')
fig.update_layout(xaxis_tickformat = "%d %B (%a)<br>%Y")
fig.show()

#%% Compute statistics
from compute_daily_variability import compute_daily_variability
X= compute_daily_variability(df_synthetic_mean_with_daily_variability['Total power (MW)'])



#%% Scale time-series to have a specifi annual energy

# Set target total energy production (in GWh):
GWh_year_target = 537

# Compute total energy produced in synthetic data:
synthetic_sample_time_hours = (df_synthetic_mean.index[1] - df_synthetic_mean.index[0]).seconds/3600
synthetic_mean_GWh_year = df_synthetic_mean['Total power (MW)'].sum() * \
                             synthetic_sample_time_hours / 1e3

# Compute scale value and apply to dataframe: 
K = GWh_year_target/synthetic_mean_GWh_year
df_synthetic_mean.loc[:,'Total power (MW)'] *= K

#%% Add time-stap to time-stamp randomness

# Initialize dataframe that will contain randomness:
df_synthetic = df_synthetic_mean.copy(deep=True)

for index, row in df_synthetic.iterrows():
    # For each row, get month, hour and type of day:
    M = row['Month']
    m = row['Time of day']
    t = row['Type of day']
    
    # Fetch std:
    std_i = df_stats.loc[(M,m,t),'std']
    
    # Add randomness from a sample of normal standard distribution (sigma=1, mean=0):
    # df_synthetic.loc[index,'Total power (MW)'] = std_i * np.random.randn() + df_synthetic_mean.loc[index,'Total power (MW)']
    
    # Fetch max and min:
    max_i =  df_stats.loc[(M,m,t),'amax']
    min_i =  df_stats.loc[(M,m,t),'amin']
    
    # Add randomness from a sample of uniform distribution :
    df_synthetic.loc[index,'Total power (MW)'] = \
        (max_i - min_i) * np.random.random_sample() -\
        (max_i - min_i)/2 + df_synthetic_mean.loc[index,'Total power (MW)']
    
        
# Compute statistical properties of synthetic data:
grouper_synthetic = df_synthetic.groupby(['Month', 'Time of day', 'Type of day'])

df_synthetic_stats = grouper_synthetic.agg([np.mean, np.std, np.median, np.max, np.min, np.count_nonzero])

# Rename indexes:
df_synthetic_stats.index = df_stats.index.set_names('Month', level=0)
df_synthetic_stats.index = df_stats.index.set_names('Time of day', level=1)

# Remove MultiIndex in column
df_synthetic_stats.columns = df_synthetic_stats.columns.droplevel(0)

#%% Verify total power in synthetic data 
# Compute total energy produced in synthetic data:
synthetic_GWh_year = df_synthetic['Total power (MW)'].sum() * \
                              synthetic_sample_time_hours / 1e3

print('Target year production (GWh): {0:0.2f}'.format(GWh_year_target))
print('Actual year production (GWh): {0:0.2f}'.format(synthetic_GWh_year))


#%% Plot synthetic data
fig = go.Figure()
fig.add_trace(go.Scatter(x=df_synthetic_mean.index,
                         y=df_synthetic_mean.loc[:,'Total power (MW)'],
                         mode='lines',
                         name= 'Total power (MW) (mean)'))

fig.add_trace(go.Scatter(x=df_synthetic.index,
                         y=df_synthetic.loc[:,'Total power (MW)'],
                         mode='lines',
                         name= 'Total power (MW) (with randomness)'))    
fig.update_layout(title='Tahti power production - Synthetic data')

fig.show()

#%% Plot synthetic data (2D plot)
n_rows = num_points_per_day  # number of points per day
# n_rows = len(df_synthetic['Time of day'].unique())  # number of points per day
n_cols = round(len(df_synthetic)/n_rows) # number of days
size_plot2D = (n_cols,n_rows)
df_synthetic_reshaped= df_synthetic['Total power (MW)'].values.reshape(size_plot2D).T

time_idx_new = pd.date_range(start=time_idx[0], 
                        end=time_idx[-1], 
                        freq='D', 
                        inclusive='left',
                        name='Date')




fig = go.Figure()
fig = px.imshow(df_synthetic_reshaped,
                labels=dict(x="Day of year", y="Hour of day", color="Total power (MW)"),
                x=time_idx_new, #list(range(1,df_synthetic_reshaped.shape[1]+1)),
                y=list(range(df_synthetic_reshaped.shape[0])),
                aspect='auto',
                origin='lower'
               )

fig.update_layout(title='Tahti power production - Synthetic data')
fig.update_xaxes(side="bottom")
fig.update_yaxes(side="left")
fig.show()


#%% Plot real data (2D plot)
year_to_plot = 2019
mask_date = data_resampled.index.year == year_to_plot

n_rows = num_points_per_day
n_cols = round(len(data_resampled[mask_date])/n_rows)

size_plot2D = (n_cols,n_rows)


data_orig = data_resampled[mask_date].values.reshape(size_plot2D).T
time_idx_orig = pd.date_range(start=data_resampled.index[mask_date][0], 
                         end=data_resampled.index[mask_date][-1], 
                         freq='D', 
                         inclusive='left',
                         name='Date')
                         
fig = go.Figure()


fig = px.imshow(data_orig,
                labels=dict(x="Day of year", y="Hour of day", color="Total power (MW)"),
                x=time_idx_orig, # list(range(data_orig.shape[1])),
                y=list(range(data_orig.shape[0])),
                aspect='auto',
                origin='lower'
               )
fig.update_layout(title='Tahti power production - Real data. Year: {0}'.format(year_to_plot))

fig.update_xaxes(side="bottom")
fig.update_yaxes(side="left")
fig.show()

#%% Plot original time-series
fig = go.Figure()

fig.add_trace(go.Scatter(x=data_resampled[mask_date].index,
                         y=data_resampled[mask_date],
                         mode='lines',
                         name= 'Total power (MW)'))

fig.update_layout(title='Tahti power production - Real data. Year: {0}'.format(year_to_plot))
fig.show()

#%%











#%% New resample:

# Compute 'df_synthetic_mean_resampled':         

# Create time index:
idx_resampled = pd.date_range(start=time_idx[0], 
                              end=time_idx[-1], 
                              freq='60 min', 
                              inclusive='left',
                              name='Date')

# Create empty dataframe:
df_synthetic_mean_resampled = pd.DataFrame(columns=['Month',
                                                    'Time of day',
                                                    'Type of day',
                                                    'Total power (MW)'],
                                           index=idx_resampled)

# Asign columns:
df_synthetic_mean_resampled.loc[:,'Month'] = df_synthetic_mean_resampled.index.month
df_synthetic_mean_resampled.loc[:,'Time of day'] = (df_synthetic_mean_resampled.index - df_synthetic_mean_resampled.index.normalize()).seconds/3600
df_synthetic_mean_resampled.loc[:,'Type of day'] = \
         df_synthetic_mean.loc[df_synthetic_mean_resampled.index,'Type of day']
df_synthetic_mean_resampled.loc[:,'Total power (MW)'] = \
         df_synthetic_mean['Total power (MW)'].resample('60 min').mean()
         
# Compute 'df_synthetic_resampled':         
df_synthetic_resampled = df_synthetic_mean_resampled.copy(deep=True)
df_synthetic_resampled.loc[:,'Total power (MW)'] = \
         df_synthetic['Total power (MW)'].resample('60 min').mean()
         
num_points_per_day_resampled = len((df_synthetic_resampled.index - df_synthetic_resampled.index.normalize()).unique())

#%% Plot synthetic data, resampled (2D plot)
n_rows = num_points_per_day_resampled  # number of points per day
n_cols = round(len(df_synthetic_resampled)/n_rows) # number of days
size_plot2D = (n_cols,n_rows)
df_synthetic_reshaped_resampled = df_synthetic_resampled['Total power (MW)'].values.reshape(size_plot2D).T

idx_day = pd.date_range(start=time_idx[0], 
                        end=time_idx[-1], 
                        freq='D', 
                        inclusive='left',
                        name='Date')

fig = go.Figure()
fig = px.imshow(df_synthetic_reshaped_resampled,
                labels=dict(x="Day of year", y="Hour of day", color="Total power (MW)"),
                x=idx_day, 
                y=list(range(df_synthetic_reshaped_resampled.shape[0])),
                aspect='auto',
                origin='lower'
               )

fig.update_layout(title='Tahti power production - Synthetic data')
fig.update_xaxes(side="bottom")
fig.update_yaxes(side="left")
fig.show()

#%% Plot synthetic data, resampled
fig = go.Figure()
fig.add_trace(go.Scatter(x=df_synthetic_mean_resampled.index,
                         y=df_synthetic_mean_resampled.loc[:,'Total power (MW)'],
                         mode='lines',
                         name= 'Total power (MW) (mean)'))

fig.add_trace(go.Scatter(x=df_synthetic_resampled.index,
                         y=df_synthetic_resampled.loc[:,'Total power (MW)'],
                         mode='lines',
                         name= 'Total power (MW) (with randomness)'))    

fig.update_layout(title='Tahti power production - Synthetic data')

fig.show()

#%% Save result to pickle file
# Set file name and path:
filename_out = r'tahiti_total_power_synthetic_{0}_{1}_GWh.pkl'.format(df_synthetic_resampled.index[0].year,
                                                                      GWh_year_target)
path_out = r'./data/' + filename_out

# Save file:
# df_synthetic_resampled.to_pickle(path_out)


#%% Plot original time-series
fig = go.Figure()

fig.add_trace(go.Scatter(x=df_SDE.index,
                          y=df_SDE.loc[:,'total_MW'],
                          mode='lines',
                          name= 'Total power (MW)'))

fig.update_layout(title='Electricity production in Tahiti - SDE')
fig.show()