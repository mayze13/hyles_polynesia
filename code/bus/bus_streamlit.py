import streamlit as st
import pandas as pd
from datetime import datetime, time
import plotly.graph_objects as go
from bus_simulation import run_hydrogen_bus_simulation

# Streamlit App Interface
st.title("Hydrogen Bus Fleet Simulation")

with st.sidebar:
    st.header("Simulation Parameters")

    # File Upload Option
    uploaded_file = st.file_uploader("Upload Parameters File (CSV or Excel)", type=["csv", "xlsx"], help="Upload a CSV or Excel file with simulation parameters. This will override any settings selected below.")

    # General Parameters
    num_buses = st.number_input("Number of Buses (Weekdays)", min_value=1, value=10, help="Total number of buses operating on weekdays.")
    trips_per_day = st.number_input("Trips per Day (Weekdays)", min_value=1, value=80, help="Total number of trips completed by the fleet on a weekday.")
    kms_per_trip = st.number_input("Kilometers per Trip", min_value=1, value=10, help="Distance covered per trip (in km).")
    avg_energy_per_km = st.number_input("Energy per km (kWh)", min_value=0.1, value=1.5, help="Average energy consumed per km (in kWh).")
    energy_std = st.number_input("Energy Std (kWh)", min_value=0.0, value=0.3, help="Standard deviation for energy consumption per km.")
    fuel_capacity = st.number_input("Fuel Capacity (kg of H2)", min_value=1, value=50, help="Maximum fuel capacity per bus (in kg of hydrogen).")
    flow_rate = st.number_input("Flow Rate (kg/min)", min_value=0.1, value=4.5, help="Refueling flow rate in kg per minute.")
    pumps_available = st.number_input("Pumps Available", min_value=1, value=2, help="Number of hydrogen pumps available for refueling.")
    time_step = st.number_input("Time Step (minutes)", min_value=1, value=15, help="Time step for each simulation interval, in minutes.")
    delta_arrival_time = st.selectbox("Gap Between Pump Usages (in time steps)", [1, 2, 3, 4], index=1, help="Multiplier for the time step gap between consecutive pump usage. For example, '2' with a 15-minute time step means a 30-minute gap.")

    # Weekday-Specific Parameters
    first_departure = st.time_input("First Departure", value=datetime.strptime("06:00", "%H:%M").time(), help="Earliest departure time for buses.")
    last_arrival = st.time_input("Last Arrival", value=datetime.strptime("22:00", "%H:%M").time(), help="Latest arrival time for buses.")
    start_date = st.date_input("Start Date", value=datetime.today(), help="Start date of the simulation.")
    days_to_predict = st.number_input("Days to Predict", min_value=1, value=7, help="Number of days the simulation will run.")

    # Saturday-Specific Parameters
    st.header("Saturday Parameters")
    saturday_buses = st.number_input("Number of Buses (Saturday)", min_value=1, value=5, help="Number of buses operating on Saturdays.")
    saturday_trips = st.number_input("Trips per Day (Saturday)", min_value=1, value=40, help="Total number of trips completed by the fleet on Saturdays.")

# Default parameters
params = {
    'num_buses': num_buses,
    'trips_per_day': trips_per_day,
    'kms_per_trip': kms_per_trip,
    'energy_per_km': avg_energy_per_km,  # Only average energy per km
    'energy_std': energy_std,  # Separate energy standard deviation
    'fuel_capacity': fuel_capacity,
    'flow_rate': flow_rate,
    'pumps_available': pumps_available,
    'time_step': time_step,
    'deltaArrivalTime': delta_arrival_time,
    'first_departure': first_departure,
    'last_arrival': last_arrival,
    'start_date': start_date,
    'days_to_predict': days_to_predict,
    'saturday_buses': saturday_buses,
    'saturday_trips': saturday_trips
}

# Override parameters with uploaded file if available
if uploaded_file:
    try:
        # Read the file based on its extension
        if uploaded_file.name.endswith(".csv"):
            data = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx"):
            data = pd.read_excel(uploaded_file)
        else:
            st.error("Invalid file type. Please upload a CSV or Excel file.")
            data = None

        # Debugging: Print out the columns for verification
        if data is not None:
            st.write("Uploaded File Columns:", list(data.columns))

        # Required columns
        required_columns = [
            'num_buses', 'trips_per_day', 'kms_per_trip', 'energy_per_km', 'energy_std',
            'fuel_capacity', 'flow_rate', 'pumps_available', 'time_step', 'deltaArrivalTime',
            'first_departure', 'last_arrival', 'start_date', 'days_to_predict',
            'saturday_buses', 'saturday_trips'
        ]

        # Verify if all columns are present
        if data is not None and set(required_columns).issubset(set(data.columns)):
            # Update parameters from the file
            params.update({
                'num_buses': int(data['num_buses'][0]),
                'trips_per_day': int(data['trips_per_day'][0]),
                'kms_per_trip': int(data['kms_per_trip'][0]),
                'energy_per_km': float(data['energy_per_km'][0]),
                'energy_std': float(data['energy_std'][0]),
                'fuel_capacity': float(data['fuel_capacity'][0]),
                'flow_rate': float(data['flow_rate'][0]),
                'pumps_available': int(data['pumps_available'][0]),
                'time_step': int(data['time_step'][0]),
                'deltaArrivalTime': int(data['deltaArrivalTime'][0]),
                'first_departure': datetime.strptime(str(data['first_departure'][0]), "%H:%M").time(),
                'last_arrival': datetime.strptime(str(data['last_arrival'][0]), "%H:%M").time(),
                'start_date': pd.to_datetime(data['start_date'][0]).date(),
                'days_to_predict': int(data['days_to_predict'][0]),
                'saturday_buses': int(data['saturday_buses'][0]),
                'saturday_trips': int(data['saturday_trips'][0])
            })
            st.success("Parameters successfully loaded from file and applied.")
        else:
            st.error("The uploaded file is missing some required columns. Please check the file format.")
    except Exception as e:
        st.error(f"Error processing file: {e}")

# Run simulation
if st.button("Run Simulation"):
    try:
        # Run the backend simulation
        result_df = run_hydrogen_bus_simulation(params)

        st.subheader("Simulation Results")
        st.dataframe(result_df)

        # Plot: Stacked area chart showing refuel load over time
        fig = go.Figure()

        for bus_id in result_df.columns:
            if bus_id != 'Total_Load':
                fig.add_trace(go.Scatter(
                    x=result_df.index,
                    y=result_df[bus_id] / 1000,  # Convert kW to MW for plotting
                    mode='lines',
                    stackgroup='one',  # Stacked area
                    name=bus_id,
                    line_shape='hv'  # Vertical steps
                ))

        fig.update_layout(
            title="Charging Load by Bus Over Time (in MW)",
            xaxis_title="Time",
            yaxis_title="Charging Load (MW)",
            legend_title="Bus ID",
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)

        # Downloadable CSV
        csv = result_df.to_csv(index=True)  # Convert DataFrame to CSV
        st.download_button(
            label="Download Simulation Data as CSV",
            data=csv,
            file_name="hydrogen_bus_simulation_results.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"Error running simulation: {e}")
