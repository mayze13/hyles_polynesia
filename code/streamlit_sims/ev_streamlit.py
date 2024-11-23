import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import ev_fleet_simulation
from datetime import datetime, time
import io

st.set_page_config(page_title='EV Fleet Simulation', layout='wide')

st.title('🚗 Electric Vehicle Fleet Simulation')

# Sidebar for User Inputs
st.sidebar.header('Simulation Parameters')

if 'simulation_name' not in st.session_state:
    st.session_state.simulation_name = f'Simulation_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
simulation_name = st.sidebar.text_input('Simulation Name', value=st.session_state.simulation_name)
st.session_state.simulation_name = simulation_name
simulation_days = st.sidebar.number_input('Simulation Days', min_value=1, max_value=365, value=7)
resample_time = st.sidebar.selectbox(
    "Time step",
    ("10T", "30T", "1H"),
)
start_date = st.sidebar.date_input('Start Date', value=datetime.now().date())
work_charging_probability = st.sidebar.slider('Work Charging Probability (%)', min_value=0.0, max_value=100.0, value=50.0, step=1.0) / 100.0
# Fleet parameters
st.sidebar.header('Fleet Parameters')
num_evs = st.sidebar.number_input('Number of BEVs', min_value=0, value=800, step=100)
num_phevs = st.sidebar.number_input('Number of PHEVs', min_value=0, value=500, step=50)
num_ldvs = st.sidebar.number_input('Number of LDVs', min_value=0, value=300, step=50)
num_two_wheelers = st.sidebar.number_input('Number of Two Wheelers', min_value=0, value=400, step=50)

# Unified Average Daily Distance Parameters
st.sidebar.header('Average Daily Distance')
daily_distance_weekday = (st.sidebar.number_input('Weekday Distance Mean (km)', value=40.0),
                          st.sidebar.number_input('Weekday Distance Std Dev (km)', value=5.0))
daily_distance_weekend = (st.sidebar.number_input('Weekend Distance Mean (km)', value=30.0),
                          st.sidebar.number_input('Weekend Distance Std Dev (km)', value=5.0))

# Randomness parameter
st.sidebar.header('Randomness Parameter')
randomness = st.sidebar.slider('Randomness (%)', min_value=0.0, max_value=100.0, value=10.0, step=1.0) / 100.0

# BEV and PHEV Parameters
st.sidebar.header('Vehicle Type Parameters')
ev_battery_capacity = st.sidebar.number_input('BEV Battery Capacity (kWh)', min_value=1.0, value=60.0)
ev_energy_consumption = st.sidebar.number_input('BEV Energy Consumption (kWh/km)', min_value=0.01, value=0.15)
phev_battery_capacity = st.sidebar.number_input('PHEV Battery Capacity (kWh)', min_value=1.0, value=12.0)
phev_energy_consumption = st.sidebar.number_input('PHEV Energy Consumption (kWh/km)', min_value=0.01, value=0.20)

# LDV and Two Wheeler Parameters
st.sidebar.header('LDV and Two Wheeler Parameters')
ldv_battery_capacity = st.sidebar.number_input('LDV Battery Capacity (kWh)', min_value=1.0, value=60.0)
ldv_energy_consumption = st.sidebar.number_input('LDV Energy Consumption (kWh/km)', min_value=0.01, value=0.20)
two_wheeler_battery_capacity = st.sidebar.number_input('Two Wheeler Battery Capacity (kWh)', min_value=0.1, value=2.2)
two_wheeler_energy_consumption = st.sidebar.number_input('Two Wheeler Energy Consumption (kWh/km)', min_value=0.001, value=0.02)

# Run Simulation Button
if st.button('Run Simulation'):
    params = {
        'simulation_days': int(simulation_days),
        'start_date': pd.Timestamp(start_date),
        'num_evs': int(num_evs),
        'num_phevs': int(num_phevs),
        'num_ldvs': int(num_ldvs),
        'num_two_wheelers': int(num_two_wheelers),
        'ev_params': {
            'battery_capacity': ev_battery_capacity,
            'energy_consumption': ev_energy_consumption
        },
        'phev_params': {
            'battery_capacity': phev_battery_capacity,
            'energy_consumption': phev_energy_consumption
        },
        'ldv_params': {
            'battery_capacity': ldv_battery_capacity,
            'energy_consumption': ldv_energy_consumption
        },
        'two_wheeler_params': {
            'battery_capacity': two_wheeler_battery_capacity,
            'energy_consumption': two_wheeler_energy_consumption
        },
        'daily_distance_weekday': daily_distance_weekday,
        'daily_distance_weekend': daily_distance_weekend,
        'home_departure_time': time(7, 0),
        'home_departure_std': 0.5,
        'work_departure_time': time(17, 0),
        'work_departure_std': 0.5,
        'randomness': randomness,
        'date_range': pd.date_range(start=pd.Timestamp(start_date), periods=simulation_days, freq='D'),
        'work_charging_probability': work_charging_probability,
        'resample_time': resample_time
    }

    # Initialize progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()

    def progress_callback(progress):
        """Callback function to update progress bar and status text."""
        progress_bar.progress(int(progress * 100))
        status_text.text(f"Simulation progress: {int(progress * 100)}%")

    # Run the simulation with progress callback
    with st.spinner('Initializing simulation...'):
        charging_events_df, load_profile, location_profile = ev_fleet_simulation.run_simulation(params, progress_callback)

    # Hide progress bar and status text when simulation is complete
    progress_bar.empty()
    status_text.empty()

    # Store results in session state
    st.session_state['charging_events_df'] = charging_events_df
    st.session_state['load_profile'] = load_profile
    st.session_state['location_profile'] = location_profile
# Check if the session state contains the data to display plots and download
if 'load_profile' in st.session_state and not st.session_state['load_profile'].empty:
    load_profile = st.session_state['load_profile']
    # Plot load profiles by vehicle type
    load_profile.reset_index(inplace=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=load_profile['timestamp'], y=load_profile['BEV_Load'],
                             mode='lines', name='BEV Load', line=dict(color='#98FB98', width=1),
                             fill='tonexty', stackgroup='one'))
    fig.add_trace(go.Scatter(x=load_profile['timestamp'], y=load_profile['PHEV_Load'],
                             mode='lines', name='PHEV Load', line=dict(color='#B39CD0', width=1),
                             fill='tonexty', stackgroup='one'))
    fig.add_trace(go.Scatter(x=load_profile['timestamp'], y=load_profile['LDV_Load'],
                             mode='lines', name='LDV Load', line=dict(color='#FFA07A', width=1),
                             fill='tonexty', stackgroup='one'))
    fig.add_trace(go.Scatter(x=load_profile['timestamp'], y=load_profile['Two_Wheeler_Load'],
                             mode='lines', name='Two Wheeler Load', line=dict(color='#87CEFA', width=1),
                             fill='tonexty', stackgroup='one'))

    fig.update_layout(
        title='Fleet Charging Load Profile Over Time',
        xaxis_title='Time',
        yaxis_title='Power Demand (kW)',
        hovermode='x unified',
        xaxis=dict(tickformat='%b %d, %H:%M'),
        yaxis=dict(ticksuffix=' kW')
    )
    st.plotly_chart(fig, use_container_width=True)

    # Add another plot for load profile by location
    location_profile = st.session_state['location_profile']
    location_profile.reset_index(inplace=True)
    fig_location = go.Figure()
    fig_location.add_trace(go.Scatter(x=location_profile['timestamp'], y=location_profile['Home_Load'],
                                      mode='lines', name='Home Load', line=dict(color='#C19A6B', width=1),
                                      fill='tonexty', stackgroup='one'))
    fig_location.add_trace(go.Scatter(x=location_profile['timestamp'], y=location_profile['Work_Load'],
                                      mode='lines', name='Work Load', line=dict(color='#4682B4', width=1),
                                      fill='tonexty', stackgroup='one'))

    fig_location.update_layout(
        title='Fleet Charging Load Profile by Location',
        xaxis_title='Time',
        yaxis_title='Power Demand (kW)',
        hovermode='x unified',
        xaxis=dict(tickformat='%b %d, %H:%M'),
        yaxis=dict(ticksuffix=' kW')
    )
    st.plotly_chart(fig_location, use_container_width=True)

    # Combine all data into a single CSV for download
    # charging_events_df = st.session_state['charging_events_df']
    # combined_data = pd.merge(charging_events_df, load_profile, left_on='timestamp', right_on='timestamp', how='outer')
    # combined_data = pd.merge(combined_data, location_profile, left_on='timestamp', right_on='timestamp', how='outer')

    st.header("Download Simulation Results")

    # Convert combined dataframe to CSV and create download link
    csv_buffer_combined = io.StringIO()
    load_profile.to_csv(csv_buffer_combined, index=False)
    st.download_button(
        label="Download Combined Results as CSV",
        data=csv_buffer_combined.getvalue(),
        file_name=f'{simulation_name}_results.csv',
        mime='text/csv'
    )
    if not location_profile.empty:
        st.header("Download Location Load Profile")
        # Creating CSV with Home_Load and Work_Load
        location_csv = location_profile.to_csv(index=False)

        # Download button for the Location load profile
        st.download_button(
            label="Download Location Load CSV",
            data=location_csv,
            file_name=f"{simulation_name}_location_load.csv",
            mime='text/csv'
        )
    # events_csv = charging_events_df.to_csv(index=False)
    # st.download_button(
    #     label="Download charging_events_df as CSV",
    #     data=events_csv,
    #     file_name=f'{simulation_name}_charging_events_df.csv',
    #     mime='text/csv'
    # )
    # charging_events_df
