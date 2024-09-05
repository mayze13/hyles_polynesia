# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 09:51:01 2024

@author: ferrucci
"""

#%% Imports
import numpy as np
import pandas as pd
import holidays
# from scipy.signal import savgol_filter
import plotly.io as pio
# import plotly.express as px
import plotly.graph_objects as go
pio.renderers.default = 'browser'
pd.options.plotting.backend = 'plotly' # Panda plotly backend.

#%%
def linear_transition(start_index, 
                      end_index, 
                      start_value, 
                      end_value, 
                      length):
    """Create a linear transition array between two values over a specified length."""
    return np.linspace(start_value, end_value, length)

#%%
from scipy.ndimage import uniform_filter1d

def smooth_vector_keeping_boundaries(vector, window_size=3):
    
    # Do nothing if window_size = 0
    if window_size == 0:
        return vector
    
    # Apply uniform filter for smoothing
    smoothed_vector = uniform_filter1d(vector, size=window_size, mode='nearest')
    
    # Manually set the first and last elements to their original values
    smoothed_vector[0] = vector[0]
    smoothed_vector[-1] = vector[-1]
    
    return smoothed_vector

#%%
def generate_ev_power_profile(time_index, 
                              plateau_morning_start, plateau_morning_end, plateau_morning_value, 
                              peak_noon_start, peak_noon_end, peak_noon_value, 
                              plateau_afternoon_start, plateau_afternoon_end, plateau_afternoon_value, 
                              peak_evening_start, peak_evening_end, peak_evening_value,
                              plateau_night_start, plateau_night_end, plateau_night_value, 
                              smooth_window_size=0
                              ):
    
    # Convert inputs to Timedelta if they are not already
    plateau_morning_start = pd.Timedelta(plateau_morning_start)
    plateau_morning_end = pd.Timedelta(plateau_morning_end)
    plateau_afternoon_start = pd.Timedelta(plateau_afternoon_start)
    plateau_afternoon_end = pd.Timedelta(plateau_afternoon_end)
    plateau_night_start = pd.Timedelta(plateau_night_start)
    plateau_night_end = pd.Timedelta(plateau_night_end)
    peak_noon_start = pd.Timedelta(peak_noon_start)
    peak_noon_end = pd.Timedelta(peak_noon_end)
    peak_evening_start = pd.Timedelta(peak_evening_start)
    peak_evening_end = pd.Timedelta(peak_evening_end)
    
    # Verify consistency of inputs:
    if plateau_morning_end > peak_noon_start:
        print('Plateau morning ends afer start of peak moon => Setting plateau_morning_end = peak_noon_start')
        plateau_morning_end = peak_noon_start
        
    if peak_noon_end > plateau_afternoon_start:
        print('Peak noon ends after start of plateau afternoon => Setting plateau_afternoon_start = peak_noon_end')
        plateau_afternoon_start = peak_noon_end
        
    if plateau_afternoon_end > peak_evening_start:
        print('Plateau afternoon ends afer start of peak evening => Setting plateau_afternoon_end = peak_evening_start')
        plateau_afternoon_end = peak_evening_start

    if peak_evening_end > plateau_night_start:
        print('Peak evening ends after start of plateau night => Setting plateau_night_start = peak_evening_end')
        plateau_night_start = peak_evening_end

    if plateau_night_end - pd.Timedelta(days=plateau_night_end.days) > plateau_morning_start:
        print('Plateau night ends after start of plateau morning => Setting plateau_night_end = plateau_morning_start + 1 day')
        plateau_night_end = plateau_morning_start  + pd.Timedelta(days=plateau_night_end.days)
        
    # Compute number of points:
    num_points = len(time_index)
    
    # Initialize the power profile with zeros
    power_profile = np.zeros(num_points)
    
    # Set the values for the plateaus
    plateau_morning_indices = (time_index >= plateau_morning_start) & (time_index <= plateau_morning_end)
    plateau_afternoon_indices = (time_index >= plateau_afternoon_start) & (time_index <= plateau_afternoon_end)
    
    plateau_night_starts_in_following_day = plateau_night_start.days >= 1
    plateau_night_extends_to_following_day = plateau_night_end.days - plateau_night_start.days >= 1
            
    if plateau_night_extends_to_following_day:
        plateau_night_indices = (time_index <= plateau_night_end - pd.Timedelta(days=1)) | \
                                (time_index >= plateau_night_start)
    else:
        # Remove 1 day if both start and end ends up in the following day:
        plateau_night_indices = (time_index >= plateau_night_start - pd.Timedelta(days=plateau_night_start.days)) & \
                                (time_index <= plateau_night_end - pd.Timedelta(days=plateau_night_end.days))
    
    power_profile[plateau_morning_indices] = plateau_morning_value
    power_profile[plateau_afternoon_indices] = plateau_afternoon_value
    power_profile[plateau_night_indices] = plateau_night_value
    
    # Set the values for the peaks
    peak_noon_indices = (time_index >= peak_noon_start) & (time_index <= peak_noon_end)
    peak_evening_indices = (time_index >= peak_evening_start) & (time_index <= peak_evening_end)
    
    power_profile[peak_noon_indices] = peak_noon_value
    power_profile[peak_evening_indices] = peak_evening_value
        
    # Set the values for linear transitions
    plateau_morning_start_index = (np.abs(time_index - plateau_morning_start)).argmin()
    plateau_morning_end_index =   (np.abs(time_index - plateau_morning_end)).argmin()
    #
    peak_noon_start_index = (np.abs(time_index - peak_noon_start)).argmin()
    peak_noon_end_index =   (np.abs(time_index - peak_noon_end)).argmin()
    #
    plateau_afternoon_start_index = (np.abs(time_index - plateau_afternoon_start)).argmin()
    plateau_afternoon_end_index =   (np.abs(time_index - plateau_afternoon_end)).argmin()
    #
    peak_evening_start_index = (np.abs(time_index - peak_evening_start)).argmin()
    peak_evening_end_index =   (np.abs(time_index - peak_evening_end)).argmin()
    #
    plateau_night_start_index = (np.abs(time_index - \
                                        (plateau_night_start - pd.Timedelta(days=plateau_night_start.days))
                                       )).argmin()
    plateau_night_end_index =   (np.abs(time_index - \
                                        (plateau_night_end - pd.Timedelta(days=plateau_night_end.days))
                                       )).argmin()

    # Transition from plateau morning to peak noon:
    transition2 = linear_transition(plateau_morning_end_index, 
                                    peak_noon_start_index, 
                                    plateau_morning_value, 
                                    peak_noon_value, 
                                    peak_noon_start_index - plateau_morning_end_index + 1)
    
    power_profile[plateau_morning_end_index:peak_noon_start_index+1] = transition2
    
    # Transition from peak noon to plateau afternoon
    transition3 = linear_transition(peak_noon_end_index, 
                                    plateau_afternoon_start_index, 
                                    peak_noon_value, 
                                    plateau_afternoon_value, 
                                    plateau_afternoon_start_index - peak_noon_end_index + 1)
    power_profile[peak_noon_end_index:plateau_afternoon_start_index+1] = transition3
    
    # Transition from plateau afernoon to peak evening:
    transition4 = linear_transition(plateau_afternoon_end_index, 
                                    peak_evening_start_index, 
                                    plateau_afternoon_value, 
                                    peak_evening_value, 
                                    peak_evening_start_index - plateau_afternoon_end_index + 1)
    power_profile[plateau_afternoon_end_index:peak_evening_start_index+1] = transition4
    
    # Transition from peak evening to pleateu night:
    if plateau_night_starts_in_following_day:        
        transition5 = linear_transition(peak_evening_end_index, 
                                        plateau_night_start_index + num_points, 
                                        peak_evening_value, 
                                        plateau_night_value, 
                                        plateau_night_start_index + num_points - peak_evening_end_index + 1)
        power_profile[peak_evening_end_index:num_points] = transition5[0:num_points-peak_evening_end_index]
        power_profile[0:plateau_night_start_index] = transition5[num_points-peak_evening_end_index+1:]
    else:
        transition5 = linear_transition(peak_evening_end_index, 
                                        plateau_night_start_index, 
                                        peak_evening_value, 
                                        plateau_night_value, 
                                        plateau_night_start_index - peak_evening_end_index + 1)
        power_profile[peak_evening_end_index:plateau_night_start_index+1] = transition5
        
        
    # if plateau_night_extends_to_following_day:             
        
    # Transition from plateau night to plateau morning
    transition1 = linear_transition(plateau_night_end_index, 
                                    plateau_morning_start_index, 
                                    plateau_night_value, 
                                    plateau_morning_value, 
                                    plateau_morning_start_index - plateau_night_end_index + 1)
    
    power_profile[plateau_night_end_index:plateau_morning_start_index+1] = transition1
    
    # Smooth the profile using a moving average
    power_profile = smooth_vector_keeping_boundaries(power_profile,
                                                     window_size=smooth_window_size)
    
    return pd.Series(power_profile, index=time_index)

#%% New function, distinguishing between previous night and current night
def generate_ev_power_profile_with_initial_condition(
                               time_index, 
                               plateau_night_value_prev, # initial condition
                               plateau_morning_start, plateau_morning_end, plateau_morning_value, 
                               peak_noon_start, peak_noon_end, peak_noon_value, 
                               plateau_afternoon_start, plateau_afternoon_end, plateau_afternoon_value, 
                               peak_evening_start, peak_evening_end, peak_evening_value,
                               plateau_night_start, plateau_night_end, plateau_night_value, 
                               smooth_window_size=0
                              ):
    
    # Convert inputs to Timedelta if they are not already
    plateau_morning_start = pd.Timedelta(plateau_morning_start)
    plateau_morning_end = pd.Timedelta(plateau_morning_end)
    peak_noon_start = pd.Timedelta(peak_noon_start)
    peak_noon_end = pd.Timedelta(peak_noon_end)
    plateau_afternoon_start = pd.Timedelta(plateau_afternoon_start)
    plateau_afternoon_end = pd.Timedelta(plateau_afternoon_end)
    peak_evening_start = pd.Timedelta(peak_evening_start)
    peak_evening_end = pd.Timedelta(peak_evening_end)
    plateau_night_start = pd.Timedelta(plateau_night_start)
    plateau_night_end = pd.Timedelta(plateau_night_end)
    
    # Verify consistency of inputs:
    if plateau_morning_end > peak_noon_start:
        print('Plateau morning ends afer start of peak moon => Setting plateau_morning_end = peak_noon_start')
        plateau_morning_end = peak_noon_start
        
    if peak_noon_end > plateau_afternoon_start:
        print('Peak noon ends after start of plateau afternoon => Setting plateau_afternoon_start = peak_noon_end')
        plateau_afternoon_start = peak_noon_end
        
    if plateau_afternoon_end > peak_evening_start:
        print('Plateau afternoon ends afer start of peak evening => Setting plateau_afternoon_end = peak_evening_start')
        plateau_afternoon_end = peak_evening_start

    if peak_evening_end > plateau_night_start:
        print('Peak evening ends after start of plateau night => Setting plateau_night_start = peak_evening_end')
        plateau_night_start = peak_evening_end

    if plateau_night_end - pd.Timedelta(days=plateau_night_end.days) > plateau_morning_start:
        print('Plateau night ends after start of plateau morning => Setting plateau_night_end = plateau_morning_start + 1 day')
        plateau_night_end = plateau_morning_start  + pd.Timedelta(days=plateau_night_end.days)
        
    # Compute number of points:
    num_points = len(time_index)
    
    # Initialize the power profile with zeros
    power_profile = np.zeros(num_points)
    
    # Set the values for the plateaux
    
    plateau_night_prev_indices = (time_index <= plateau_night_end)
    plateau_morning_indices = (time_index >= plateau_morning_start) & (time_index <= plateau_morning_end)
    plateau_afternoon_indices = (time_index >= plateau_afternoon_start) & (time_index <= plateau_afternoon_end)
    plateau_night_indices = (time_index >= plateau_night_start)
    
    power_profile[plateau_morning_indices] = plateau_morning_value
    power_profile[plateau_afternoon_indices] = plateau_afternoon_value
    power_profile[plateau_night_prev_indices] = plateau_night_value_prev
    power_profile[plateau_night_indices] = plateau_night_value
    
    # Set the values for the peaks
    peak_noon_indices = (time_index >= peak_noon_start) & (time_index <= peak_noon_end)
    peak_evening_indices = (time_index >= peak_evening_start) & (time_index <= peak_evening_end)
    
    power_profile[peak_noon_indices] = peak_noon_value
    power_profile[peak_evening_indices] = peak_evening_value
        
    # Set the values for linear transitions
    plateau_morning_start_index = (np.abs(time_index - plateau_morning_start)).argmin()
    plateau_morning_end_index =   (np.abs(time_index - plateau_morning_end)).argmin()
    #
    peak_noon_start_index = (np.abs(time_index - peak_noon_start)).argmin()
    peak_noon_end_index =   (np.abs(time_index - peak_noon_end)).argmin()
    #
    plateau_afternoon_start_index = (np.abs(time_index - plateau_afternoon_start)).argmin()
    plateau_afternoon_end_index =   (np.abs(time_index - plateau_afternoon_end)).argmin()
    #
    peak_evening_start_index = (np.abs(time_index - peak_evening_start)).argmin()
    peak_evening_end_index =   (np.abs(time_index - peak_evening_end)).argmin()
    #
    plateau_night_start_index = (np.abs(time_index - plateau_night_start)).argmin()
    plateau_night_end_index =   (np.abs(time_index -  plateau_night_end)).argmin()

    # Transition from plateau morning to peak noon:
    transition2 = linear_transition(plateau_morning_end_index, 
                                    peak_noon_start_index, 
                                    plateau_morning_value, 
                                    peak_noon_value, 
                                    peak_noon_start_index - plateau_morning_end_index + 1)
    
    power_profile[plateau_morning_end_index:peak_noon_start_index+1] = transition2
    
    # Transition from peak noon to plateau afternoon
    transition3 = linear_transition(peak_noon_end_index, 
                                    plateau_afternoon_start_index, 
                                    peak_noon_value, 
                                    plateau_afternoon_value, 
                                    plateau_afternoon_start_index - peak_noon_end_index + 1)
    power_profile[peak_noon_end_index:plateau_afternoon_start_index+1] = transition3
    
    # Transition from plateau afernoon to peak evening:
    transition4 = linear_transition(plateau_afternoon_end_index, 
                                    peak_evening_start_index, 
                                    plateau_afternoon_value, 
                                    peak_evening_value, 
                                    peak_evening_start_index - plateau_afternoon_end_index + 1)
    power_profile[plateau_afternoon_end_index:peak_evening_start_index+1] = transition4
    
    # Transition from peak evening to pleateu night:
    transition5 = linear_transition(peak_evening_end_index, 
                                    plateau_night_start_index, 
                                    peak_evening_value, 
                                    plateau_night_value, 
                                    plateau_night_start_index - peak_evening_end_index + 1)
    power_profile[peak_evening_end_index:plateau_night_start_index+1] = transition5
        
    # Transition from plateau night to plateau morning
    transition1 = linear_transition(plateau_night_end_index, 
                                    plateau_morning_start_index, 
                                    plateau_night_value_prev, 
                                    plateau_morning_value, 
                                    plateau_morning_start_index - plateau_night_end_index + 1)
    
    power_profile[plateau_night_end_index:plateau_morning_start_index+1] = transition1
    
    # Smooth the profile using a moving average
    power_profile = smooth_vector_keeping_boundaries(power_profile,
                                                     window_size=smooth_window_size)
    
    return pd.Series(power_profile, index=time_index)


#%% Compute daily MWh
def compute_daily_MWh(power_profile):
    
    dT_seconds = power_profile.index.freq.nanos/1e9
    dT_hours = dT_seconds/3600
    mwh = power_profile.sum() * dT_hours
    
    return mwh

#%% Example usage

i_want_to_run_example_of_usage = True

if i_want_to_run_example_of_usage:
    # time_index = pd.to_timedelta(np.arange(0, 24, 1), unit='h')
    time_index = pd.date_range(start='01-Jan-2000 00:00:00',
                               end=  '02-Jan-2000 00:00:00',
                               freq='5min',
                               inclusive='left')
    time_index = time_index - time_index[0]
    
    plateau_morning_start = '06:00:00'
    plateau_morning_end =   '11:00:00'
    plateau_morning_value = 0.15
    
    peak_noon_start = '12:00:00'
    peak_noon_end =   '12:40:00'
    peak_noon_value = 0.2
    
    plateau_afternoon_start = '13:40:00'
    plateau_afternoon_end =   '17:30:00'
    plateau_afternoon_value = 0.15
    
    peak_evening_start = '19:30:00'
    peak_evening_end =   '20:40:00'
    # peak_evening_end =   '1 day 00:30:00'
    peak_evening_value = 0.7
    
    # plateau_night_start = '23:00:00'
    plateau_night_start = '1 day 2:30:00'
    plateau_night_end =   '1 day 4:00:00'
    plateau_night_value = 0.1
    
    # Compute profile:
    power_profile = generate_ev_power_profile(
        time_index,
        plateau_morning_start, plateau_morning_end, plateau_morning_value, 
        peak_noon_start, peak_noon_end, peak_noon_value, 
        plateau_afternoon_start, plateau_afternoon_end, plateau_afternoon_value, 
        peak_evening_start, peak_evening_end, peak_evening_value,
        plateau_night_start, plateau_night_end, plateau_night_value, 
        smooth_window_size = 5
        )
    
    # Plot:
    power_profile.index = pd.to_datetime('01-Jan-2024 00:00:00') + power_profile.index 
    power_profile.plot(kind='line').show()
    # power_profile.plot(kind='bar').show()
    print(compute_daily_MWh(power_profile))
    
#%% Example usage 2

i_want_to_run_example_of_usage = True

if i_want_to_run_example_of_usage:
    # time_index = pd.to_timedelta(np.arange(0, 24, 1), unit='h')
    time_index = pd.date_range(start='01-Jan-2000 00:00:00',
                               end=  '02-Jan-2000 00:00:00',
                               freq='5min',
                               inclusive='left')
    time_index = time_index - time_index[0]
    

    plateau_night_end =   '4:00:00'
    plateau_night_value_prev = 0.1

    plateau_morning_start = '06:00:00'
    plateau_morning_end =   '11:00:00'
    plateau_morning_value = 0.20
    
    peak_noon_start = '12:00:00'
    peak_noon_end =   '12:40:00'
    peak_noon_value = 0.35
    
    plateau_afternoon_start = '13:40:00'
    plateau_afternoon_end =   '17:30:00'
    plateau_afternoon_value = 0.15
    
    peak_evening_start = '19:30:00'
    peak_evening_end =   '20:40:00'
    # peak_evening_end =   '1 day 00:30:00'
    peak_evening_value = 0.7
    
    plateau_night_start = '23:00:00'
    # plateau_night_start = '1 day 2:30:00'
    plateau_night_value = 0.3
    
    # Compute profile:
    power_profile = generate_ev_power_profile_with_initial_condition(
        time_index,
        plateau_night_value_prev,
        plateau_morning_start, plateau_morning_end, plateau_morning_value, 
        peak_noon_start, peak_noon_end, peak_noon_value, 
        plateau_afternoon_start, plateau_afternoon_end, plateau_afternoon_value, 
        peak_evening_start, peak_evening_end, peak_evening_value,
        plateau_night_start, plateau_night_end, plateau_night_value, 
        smooth_window_size=0,
        )
    
    # Plot:
    power_profile.index = pd.to_datetime('01-Jan-2024 00:00:00') + power_profile.index 
    power_profile.plot(kind='line').show()
    # power_profile.plot(kind='bar').show()
    print(compute_daily_MWh(power_profile))

#%%

def compute_ev_power_profile_parameters(df_param_power, current_date):
    
    # Compute day type:
    holidays_polynesia = holidays.country_holidays('FR', subdiv='Polynésie Française')
    if current_date.normalize() in holidays_polynesia:
        day_type = 'Sunday/Holiday'
    else:
        if current_date.dayofweek < 5:
            day_type = 'Weekday'
        elif current_date.dayofweek == 5:         
            day_type = 'Saturday'
        elif current_date.dayofweek == 6:
            day_type = 'Saturday'
        else:
            print('Error! Shouldn''t be here!')
    
    # Compute evening peak:
    max = df_param_power.loc[:,('next_rel_max_value', day_type)].max()
    peak_evening_value = \
        df_param_power.loc[current_date.month,('next_rel_max_value', day_type)]/max

    peak_evening_start = \
        df_param_power.loc[current_date.month,('next_rel_max_index', day_type)] \
        - pd.Timedelta('00:30:00')   

    peak_evening_end = \
        df_param_power.loc[current_date.month,('next_rel_max_index', day_type)] \
        + pd.Timedelta('00:30:00')   
    
    # Compute noon peak:
    max = df_param_power.loc[:,('first_rel_max_value', day_type)].max()
    peak_noon_value = \
        df_param_power.loc[current_date.month,('first_rel_max_value', day_type)]/max/5
    
    peak_noon_start = \
        df_param_power.loc[current_date.month,('first_rel_max_index', day_type)] \
        - pd.Timedelta('00:30:00')   
    
    peak_noon_end = \
        df_param_power.loc[current_date.month,('first_rel_max_index', day_type)] \
        + pd.Timedelta('00:30:00')   
        
    # Compute night plateau:
        
        
    # Compute morning plateau:

    # Compute afternoon plateau:
        

    plateau_morning_start = "05:00:00"
    plateau_morning_end = "11:00:00"
    plateau_morning_value = 0.35
    peak_noon_start = "12:00:00"
    peak_noon_end = "13:00:00"
    peak_noon_value = 0.4
    plateau_afternoon_start = "14:00:00"
    plateau_afternoon_end = "17:30:00"
    plateau_afternoon_value = 0.3
    peak_evening_start = "18:30:00"
    peak_evening_end = "20:00:00"
    peak_evening_value = 0.7
    plateau_night_start = "22:00:00"
    plateau_night_end = "1 day 02:00:00"
    plateau_night_value = 0.1
        
    return {
        'plateau_morning_start': plateau_morning_start,
        'plateau_morning_end': plateau_morning_end,
        'plateau_morning_value': plateau_morning_value,
        'peak_noon_start': peak_noon_start,
        'peak_noon_end': peak_noon_end,
        'peak_noon_value': peak_noon_value,
        'plateau_afternoon_start': plateau_afternoon_start,
        'plateau_afternoon_end': plateau_afternoon_end,
        'plateau_afternoon_value': plateau_afternoon_value,
        'peak_evening_start': peak_evening_start,
        'peak_evening_end': peak_evening_end,
        'peak_evening_value': peak_evening_value,
        'plateau_night_start': plateau_night_start,
        'plateau_night_end': plateau_night_end,
        'plateau_night_value': plateau_night_value,
    }

#%% Create yearly profile

def compute_yearly_profile(path_profile_param,
                           year_to_synthetize=2024,
                           smooth_window_size=0,
                           plot_enable=True,
                           debug_enable=False):
    
    # Import dataframe with charasteristics of power profile at Tahiti:
    df_param_power = pd.read_pickle(path_profile_param)
    
    # Create time index:
    time_idx = pd.date_range(start='01-Jan-' + str(year_to_synthetize), 
                        # end='08-Jan-' + str(year_to_synthetize),
                        end='01-Jan-' + str(year_to_synthetize+1),
                        # freq='10 min', 
                        freq='60 min', 
                        inclusive='left',
                        name='Date')
    
    # Create empty dataframe:
    df = pd.DataFrame(columns=['EV_power_MW'],
                      index=time_idx,
                      dtype='float64')
    
    # Day-by-day itereation, filling up the dataframe:
    
    # Initialize daily timedelta index (which is an argument of 
    # 'generate_ev_power_profile' function):
    daily_time_index =pd.timedelta_range(start='0 day 00:00:00', 
                                         end=  '1 day 00:00:00', 
                                         freq=time_idx.freq, 
                                         closed='left')    
    
    # Crete grouper to iterate day-by-day:
    grouper_daily = df.groupby(df.index.normalize())
    
    # Initialize random generator
    rng = np.random.RandomState()
    
    # Initial conditions:
    is_initial_condition = True # initial condition flag, starts in 'True'
    plateau_night_value_prev_init = 0.1
    
    # Initialize variable to carry 'plateau_night_value' from one day to the other:
    plateau_night_value_prev_next = 0.0
    
    # Loop over each day:
    for current_date,this_df in grouper_daily:
                
        # Compute day type:
        holidays_polynesia = holidays.country_holidays('FR', subdiv='Polynésie Française')
        if current_date.normalize() in holidays_polynesia:
            day_type = 'Sunday/Holiday'
        else:
            if current_date.dayofweek < 5:
                day_type = 'Weekday'
            elif current_date.dayofweek == 5:         
                day_type = 'Saturday'
            elif current_date.dayofweek == 6:
                day_type = 'Saturday'
            else:
                print('Error! Shouldn''t be here!')
        
        # Morning plateau start ************************
        # Morning plateau starts around between min and max daily power consomption.
        plateau_morning_start_mean = \
            (df_param_power.loc[current_date.month,('min_index', day_type)] + \
            df_param_power.loc[current_date.month,('first_rel_max_index', day_type)])/2
        # Set standard deviation
        plateau_morning_start_std_minutes = 30
        # Compute randomness:
        dT_rnd = pd.to_timedelta(np.round(plateau_morning_start_std_minutes*rng.randn()),'m')
        # Compute final falue:
        plateau_morning_start = plateau_morning_start_mean + dT_rnd
        
        # Morning plateau end time *********************
        plateau_morning_end = '12:00:00'
        
        # Noon peak start time *************************
        peak_noon_start = plateau_morning_end
        
        # Noon peak end time ***************************
        peak_noon_end = peak_noon_start
        
        # Afternoon plateau start time *****************
        plateau_afternoon_start = peak_noon_end
                
        # Afternoon plateau end time *******************
        # Afternoon plateau ends around the time of the afternoon minimal consomption
        # during afternoon.
        plateau_afternoon_end_mean = \
            df_param_power.loc[current_date.month,('next_rel_min_index', day_type)]
        # Set standard deviation for the end of plateau:
        plateau_afternoon_end_std_minutes = 10
        # Compute randomness:
        dT_rnd = pd.to_timedelta(np.round(plateau_afternoon_end_std_minutes*rng.randn()),'m')
        # Compute final falue:
        plateau_afternoon_end = plateau_afternoon_end_mean + dT_rnd

        # Evening peak start time *********************
        # Evening peak starts around evening max consomption.
        peak_evening_start_mean = \
            df_param_power.loc[current_date.month,('next_rel_max_index', day_type)]
        # Set standard deviation for the end of plateau:
        peak_evening_start_std_minutes = 10
        # Compute randomness:
        dT_rnd = pd.to_timedelta(np.round(peak_evening_start_std_minutes*rng.randn()),'m')
        # Compute final falue:
        peak_evening_start = peak_evening_start_mean + dT_rnd

        # Evening peak end time ************************
        # Evening peak ends X hours after start, where mean(X) is fixed by user.
        peak_evening_duration_minutes_mean = 1*60 # 4 hours
        peak_evening_duration_minutes_std = 20
        # Compute randomness:
        dT_rnd = pd.to_timedelta(np.round(peak_evening_duration_minutes_std*rng.randn()),'m')
        # Compute final value:
        peak_evening_end = \
            peak_evening_start + dT_rnd + \
            pd.to_timedelta(peak_evening_duration_minutes_mean, 'm') 
        
        # Night plateau start time *********************
        # Night plateau starts X hours after evening peak ends, where mean(X) is fixed by user.
        transition_from_evening_to_night_duration_minutes_mean = 1*60
        transition_from_evening_to_night_duration_minutes_std = 20
        # Compute randomness:
        dT_rnd = pd.to_timedelta(np.round(transition_from_evening_to_night_duration_minutes_std*rng.randn()),'m')
        # Compute final value:
        plateau_night_start = \
            peak_evening_end + dT_rnd + \
            pd.to_timedelta(transition_from_evening_to_night_duration_minutes_mean, 'm') 
            
        # Night plateau end time *********************
        # Night plateau ends around minimal consumption.
        plateau_night_end_std_minutes = 10
        plateau_night_end_mean = \
            df_param_power.loc[current_date.month,('min_index', day_type)]
        # Compute randomness:
        dT_rnd = pd.to_timedelta(np.round(plateau_night_end_std_minutes*rng.randn()),'m')
        # Compute final falue:
        # plateau_night_end = pd.to_timedelta(1,'d') + plateau_night_end_mean + dT_rnd
        plateau_night_end = plateau_night_end_mean + dT_rnd
        
        # Morning plateau value ***********************
        
        
        # Noon peak value *****************************
        
        
        # Afternoon plateau value *********************
        
        
        # Evening peak value **************************
        # Peak value is normalized to the max average daily power
        # Set standard deviation:
        peak_evening_value_std = 0.025
        # Normalize power, linear interpolation betwen max, min and current power:        
        p_max = df_param_power.loc[slice(None),('next_rel_max_value', day_type)].max()
        p_min = df_param_power.loc[slice(None),('next_rel_max_value', day_type)].min()
        p_curr = df_param_power.loc[current_date.month,('next_rel_max_value', day_type)]
        p = (p_curr-p_min)/(p_max-p_min)
        # Compute randomness:
        dp_rnd = peak_evening_value_std*rng.randn()
        peak_evening_value = p + dp_rnd
        
        # Night plateau value *************************    
        

        # Compute noon peak:

        # plateau_morning_start = "05:00:00"
        # plateau_morning_end = "11:00:00"
        plateau_morning_value = max(0.35 + 0.05*rng.randn(),0)
        # peak_noon_start = "12:00:00"
        # peak_noon_end = "13:00:00"
        peak_noon_value = plateau_morning_value
        # plateau_afternoon_start = "14:00:00"
        # plateau_afternoon_end = "17:30:00"
        plateau_afternoon_value = plateau_morning_value
        # peak_evening_start = "18:30:00"
        # peak_evening_end = "20:00:00"
        peak_evening_value = 0.7 + 0.1*rng.randn()
        # plateau_night_start = "22:00:00"
        # plateau_night_end = "1 day 02:00:00"
        plateau_night_value = max(0.45  + 0.05*rng.randn(),0)
        
        # Update 'plateau_night_value_prev':
        if is_initial_condition:
            plateau_night_value_prev = plateau_night_value_prev_init
            is_initial_condition = False # disable initial condition flag
        else:
            plateau_night_value_prev = plateau_night_value_prev_next
        
        # Update 'plateau_night_value_prev_next'
        plateau_night_value_prev_next = plateau_night_value
        
        # Compute daily profile:
        this_power_profile = generate_ev_power_profile_with_initial_condition(
            daily_time_index,
            plateau_night_value_prev,
            plateau_morning_start,
            plateau_morning_end,
            plateau_morning_value,
            peak_noon_start,
            peak_noon_end,
            peak_noon_value,
            plateau_afternoon_start,
            plateau_afternoon_end,
            plateau_afternoon_value,
            peak_evening_start,
            peak_evening_end,
            peak_evening_value,
            plateau_night_start,
            plateau_night_end, 
            plateau_night_value, 
            smooth_window_size = 0,
        )
        
        # Add instantaneaous randomness:
        instantantaneous_std = 0.00
        this_noise = instantantaneous_std*rng.randn(daily_time_index.shape[0])
        this_power_profile = this_power_profile + this_noise
        
        # Assign ev daily profile to year dataframe:
        df.loc[this_df.index,'EV_power_MW'] = this_power_profile.values
    
        # Debug information:
        if debug_enable:
            print('------------------------------')
            print('Day ' + str(current_date))
            print('plateau_morning_start = ' + str(plateau_morning_start))
            # print('plateau_morning_end = ' + str(plateau_morning_end))
            # print('plateau_morning_value = ' + str(plateau_morning_value))
            # print('peak_noon_start = ' + str(peak_noon_start))
            # print('peak_noon_end = ' + str(peak_noon_end))
            # print('peak_noon_value = ' + str(peak_noon_value))
            # print('plateau_afternoon_start = ' + str(plateau_afternoon_start))
            print('plateau_afternoon_end = ' + str(plateau_afternoon_end))
            # print('plateau_afternoon_value = ' + str(plateau_afternoon_value))
            print('peak_evening_start = ' + str(peak_evening_start))
            print('peak_evening_end = ' + str(peak_evening_end))
            # print('peak_evening_value = ' + str(peak_evening_value))
            print('plateau_night_start = ' + str(plateau_night_start))
            print('plateau_night_end = ' + str(plateau_night_end))
            # print('plateau_night_value = ' + str(plateau_night_value))

    # Smooth the profile using a moving average
    smooth = smooth_vector_keeping_boundaries(df['EV_power_MW'].values, window_size=smooth_window_size)
    df['EV_power_MW'] = smooth
    
    # Plot:
    if plot_enable:
        df.plot().show()
        # df.plot(kind='bar').show()
   
    return df

#%% Compute fraction of total yearly energy, month by month

def compute_montly_energy_fraction(path, plot_enable=True):

    # Import dataframe:
    df_SDE = pd.read_pickle(path)
    
    data_orig = df_SDE['total_MW']
    data_orig.name = 'Total power (MW)'
    data_orig.index.name = 'Date'
    
    # Get time step:
    dT = data_orig.index[1]-data_orig.index[0]
    dT_minutes = dT.seconds/60
    dT_hours = dT_minutes/60
    
    # Remove days with NaN:
    # Check NaN:
    df_nan = data_orig.isna()
    df_nan.name = 'Is NaN'
    
    # Create the mask of days where there is at least one NaN:
    mask_NaN = df_nan.groupby(df_nan.index.normalize()).transform('any')
    mask_NaN.name = 'Mask'
    
    # Apply the mask to the dataframe:
    data = data_orig[~mask_NaN]
    
    # Compute monthly energy produced:
    
    # Create group:
    grouper1 = data.groupby([data.index.year, data.index.month])
    
    # Dataframe with monthly energy:
    monthly_GWh = grouper1.sum()*dT_hours/1000
    monthly_GWh.name = 'Monthly energy (GWh)'
    monthly_GWh.index.names = ['Year','Month']
    
    # Annual energy production:
    annual_energy_GWh = data.groupby(data.index.year).sum()*dT_hours/1000
    
    # Initialize dataframe with monthly fraction of total annual energy production:
    monthly_fraction = monthly_GWh.copy(deep=True)
    monthly_fraction.name = 'Monthly fraction'
        
    # Compute fraction, month-per-month and year-per-year
    for name, group in monthly_fraction.groupby('Year'):
        monthly_fraction.loc[name, :] = group/annual_energy_GWh[name]
    
    # Plot:
    # Plot montly energy (absolute)
    if plot_enable:
        fig = go.Figure()
        for name, group in monthly_GWh.groupby('Year'):
            fig.add_trace(go.Bar(x=group.index.get_level_values('Month'),
                                 y=group,
                                 name=name))
            
        title_str = 'Monthly energy production (2015-2020) (GWh)'
        fig.update_layout(title=title_str)
        fig.show()
        
        # Plot fraction
        fig = go.Figure()
        for name, group in monthly_fraction.groupby('Year'):
            fig.add_trace(go.Bar(x=group.index.get_level_values('Month'),
                                 y=group,
                                 name=name))
        
        title_str = 'Monthly fraction of annual energy production (2015-2020)'
        fig.update_layout(title=title_str)
        fig.show()

    # Compute the average for every month, taking into account for all years:
    monthly_fraction_mean =  monthly_fraction.groupby('Month').mean()
    monthly_energy_mean = monthly_GWh.groupby('Month').mean()

    return monthly_fraction_mean, monthly_energy_mean

#%% END OF FUNCTIONS !


#%% Compute average monthly energy consumption:
path = r"./../../../../data/pkl/EDT_Tahiti_2015_2022.pkl"
(monthly_energy_fraction_mean, monthly_energy_mean_GWh) = \
    compute_montly_energy_fraction(path,
                                   plot_enable=False)
# Plot:
# monthly_energy_mean.plot(kind='bar').show()

# Set EV monthly energy consumption as a percentage of mean grid energy consumption:
ev_percentage_GWh_GWh = 0.1
ev_monthly_consumption_GWh = monthly_energy_mean_GWh * ev_percentage_GWh_GWh

#%% Example: compute yearly profile

# Import dataframe with charasteristics of power profile at Tahiti:
path = r"./../../../../data/pkl/EDT_Tahiti_2015_2022_power_profile_parameters.pkl"
df_ev = compute_yearly_profile(path,
                               year_to_synthetize=2030,
                               smooth_window_size=0,
                               plot_enable=True,
                               debug_enable=False)

energy_total_GWh = 10
energy_monthly_fraction = monthly_energy_fraction_mean




#%%     
# # Generate ev power profile:
# this_power_profile = generate_ev_power_profile(
#     daily_time_index,
#     p_ev['plateau_morning_start'],
#     p_ev['plateau_morning_end'],
#     p_ev['plateau_morning_value'],
#     p_ev['peak_noon_start'],
#     p_ev['peak_noon_end'],
#     p_ev['peak_noon_value'],
#     p_ev['plateau_afternoon_start'],
#     p_ev['plateau_afternoon_end'],
#     p_ev['plateau_afternoon_value'],
#     p_ev['peak_evening_start'],
#     p_ev['peak_evening_end'],
#     p_ev['peak_evening_value'],
#     p_ev['plateau_night_start'],
#     p_ev['plateau_night_end'], 
#     p_ev['plateau_night_value'], 
#     smooth_window_size = 10,
#     )

# Add instantaneous randomness:

# # Compute ev power profile parameters for the current day:
# p_ev = compute_ev_power_profile_parameters(df_param_power, current_date)
        
