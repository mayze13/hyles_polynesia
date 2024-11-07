import numpy as np
import pandas as pd
from datetime import timedelta, datetime
import os
import sys
import argparse
import pathlib
import plotly.graph_objects as go

class HydrogenBus:
    def __init__(self, bus_id, trips_per_bus, kms_per_trip, energy_per_km, fuel_capacity, flow_rate):
        """
        Represents a hydrogen-powered bus, tracking fuel consumption and refueling.

        Parameters:
        - bus_id (str): Unique identifier for the bus.
        - trips_per_bus (int): Number of trips this bus completes in a day.
        - kms_per_trip (int): Distance of each trip in kilometers.
        - energy_per_km (tuple): Tuple (average energy per km in kWh, standard deviation).
        - fuel_capacity (float): Maximum hydrogen fuel capacity in kilograms.
        - flow_rate (float): Refueling flow rate in kg/min.
        """
        self.bus_id = bus_id
        self.trips_per_bus = trips_per_bus
        self.kms_per_trip = kms_per_trip
        self.energy_per_km = energy_per_km  # Tuple (flat rate per km, std deviation per km)
        self.fuel_capacity = fuel_capacity
        self.state_of_fuel = fuel_capacity
        self.flow_rate = flow_rate
        self.next_available_time = None

    def simulate_day_driving(self):
        """
        Simulates a day of driving for the bus, tracking energy usage and fuel depletion.

        Returns:
        - daily_energy_consumed (float): Total energy consumed in kWh for the day.
        """
        self.state_of_fuel = self.fuel_capacity
        daily_energy_consumed = 0
        for _ in range(self.trips_per_bus):
            trip_energy = sum(
                max(0, np.random.normal(self.energy_per_km[0], self.energy_per_km[1]))
                for _ in range(self.kms_per_trip)
            )
            daily_energy_consumed += trip_energy
            self.state_of_fuel -= trip_energy / 33.33
            self.state_of_fuel = max(0, self.state_of_fuel)
        return daily_energy_consumed

    def incremental_charge(self, time_step_minutes):
        """
        Increments fuel in the bus based on the flow rate until fuel capacity is reached.

        Parameters:
        - time_step_minutes (int): The length of each charging increment in minutes.

        Returns:
        - actual_charge (float): The amount of hydrogen (kg) added during this increment.
        """
        hydrogen_to_add = self.flow_rate * time_step_minutes
        remaining_capacity = self.fuel_capacity - self.state_of_fuel
        actual_charge = min(hydrogen_to_add, remaining_capacity)
        self.state_of_fuel += actual_charge
        return actual_charge


def run_hydrogen_bus_simulation(params, output_path=None, plot_path=None):
    """
    Runs a simulation for a fleet of hydrogen buses, calculating daily driving and refueling.

    Parameters:
    - params (dict): Dictionary of simulation parameters.

    Returns:
    - simulation_df (DataFrame): Simulation data for all buses and total load.
    """
    time_step = pd.Timedelta(minutes=params['time_step'])
    time_step_minutes = params['time_step']
    delta_time = params['deltaArrivalTime'] * time_step_minutes  # Gap in minutes between each bus's charging session
    simulation_data = []

    for day in pd.date_range(start=params['start_date'], periods=params['days_to_predict']):
        if day.weekday() == 6:  # No buses run on Sundays
            continue
        elif day.weekday() == 5:  # Reduced fleet on Saturdays
            num_buses = params['saturday_buses']
            trips_per_day = params['saturday_trips']
        else:
            num_buses = params['num_buses']
            trips_per_day = params['trips_per_day']

        base_trips = trips_per_day // num_buses
        extra_trips = trips_per_day % num_buses

        buses = []
        for i in range(num_buses):
            trips_per_bus = base_trips + (1 if i < extra_trips else 0)
            bus = HydrogenBus(
                bus_id=f'Bus_{i+1}',
                trips_per_bus=trips_per_bus,
                kms_per_trip=params['kms_per_trip'],
                energy_per_km=(params['energy_per_km'], params['energy_std']),
                fuel_capacity=params['fuel_capacity'],
                flow_rate=params['flow_rate']
            )
            buses.append(bus)

        pumps_available = params['pumps_available']
        day_data = []

        # Generate timestamps for the entire day, including every time step
        full_day_time_series = pd.date_range(
            start=datetime.combine(day, params['first_departure']),
            end=datetime.combine(day + timedelta(days=1), params['first_departure']),
            freq=time_step
        )

        charging_start_time = datetime.combine(day, params['last_arrival']) + timedelta(hours=1)
        charging_end_time = datetime.combine(day + timedelta(days=1), params['first_departure'])

        charging_time_series = pd.date_range(
            start=charging_start_time,
            end=charging_end_time,
            freq=time_step
        )

        refuel_queue = []
        for bus in buses:
            bus.simulate_day_driving()
            if bus.state_of_fuel < bus.fuel_capacity:
                bus.next_available_time = charging_start_time
                refuel_queue.append(bus)

        pump_next_available_time = [charging_start_time for _ in range(pumps_available)]

        # Iterate through the full day time series
        for ts in full_day_time_series:
            load_data = {'timestamp': ts}

            # Initialize load for all buses to 0 at each time step
            for bus in buses:
                load_data[bus.bus_id] = 0

            # If within charging hours, update the load data
            if charging_start_time <= ts <= charging_end_time:
                for i in range(pumps_available):
                    if pump_next_available_time[i] <= ts and refuel_queue:
                        bus = refuel_queue.pop(0)
                        active_load = bus.incremental_charge(time_step_minutes)
                        load_kw = active_load * 33.33 / (time_step_minutes / 60)

                        load_data[bus.bus_id] = load_kw
                        pump_next_available_time[i] = ts + timedelta(minutes=delta_time)

                        if bus.state_of_fuel < bus.fuel_capacity:
                            refuel_queue.append(bus)

            # Calculate total load as the sum of individual loads
            load_data['Total_Load'] = sum(load_data[bus.bus_id] for bus in buses)
            day_data.append(load_data)

        simulation_data.extend(day_data)

    simulation_df = pd.DataFrame(simulation_data)
    simulation_df.set_index('timestamp', inplace=True)

    if output_path:
        simulation_df.to_csv(output_path)

    if plot_path:
        fig = go.Figure()
        # Plot each bus line in a separate color with markers and lines, using all buses from the DataFrame columns
        for column in simulation_df.columns:
            if column != 'Total_Load':
                fig.add_trace(go.Scatter(
                    x=simulation_df.index,
                    y=simulation_df[column],
                    mode='lines+markers',
                    name=column,
                    connectgaps=False  # Do not connect gaps in the data
                ))

        # Plot the total load
        fig.add_trace(go.Scatter(
            x=simulation_df.index,
            y=simulation_df['Total_Load'],
            mode='lines',
            name='Total Load',
            line=dict(width=2, dash='dash'),
            connectgaps=False  # Do not connect gaps in the data
        ))

        fig.update_layout(title='Hydrogen Bus Fleet Load Over Time',
                          xaxis_title='Time',
                          yaxis_title='Load (kW)',
                          hovermode='x unified')
        fig.write_html(plot_path)

    return simulation_df


def main(input_file, output_name):
    output_dir = pathlib.Path('./output')
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{output_name}.csv"
    plot_file = output_dir / f"{output_name}.html"

    if input_file.endswith('.csv'):
        params_df = pd.read_csv(input_file)
    elif input_file.endswith('.xlsx'):
        params_df = pd.read_excel(input_file)
    else:
        raise ValueError("Input file must be either .csv or .xlsx")

    params = params_df.iloc[0].to_dict()
    params['first_departure'] = datetime.strptime(params['first_departure'], "%H:%M").time()
    params['last_arrival'] = datetime.strptime(params['last_arrival'], "%H:%M").time()
    params['start_date'] = pd.to_datetime(params['start_date']).date()

    simulation_df = run_hydrogen_bus_simulation(params, output_file, plot_file)
    print(f"Simulation complete. Output saved to {output_file} and plot saved to {plot_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Hydrogen Bus Fleet Simulation')
    parser.add_argument('input_file', type=str, help='Path to the input CSV or XLSX file')
    parser.add_argument('output_name', type=str, help='Base name for output files (CSV and HTML)')
    args = parser.parse_args()

    main(args.input_file, args.output_name)
