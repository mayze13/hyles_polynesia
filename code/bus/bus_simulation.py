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
    Runs a simulation for a fleet of hydrogen buses, calculating daily driving, refueling, and production load.

    Parameters:
    - params (dict): Dictionary of simulation parameters.

    Returns:
    - simulation_df (DataFrame): Simulation data for all buses and total load.
    """
    time_step = pd.Timedelta(minutes=params['time_step'])
    time_step_minutes = params['time_step']
    delta_time = params['deltaArrivalTime'] * time_step_minutes  # Gap in minutes between each bus's charging session
    production_efficiency = params.get('production_efficiency', 55)  # kWh per kg of hydrogen produced (default 55)
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
                        active_charge = bus.incremental_charge(time_step_minutes)
                        dispensing_load_kw = active_charge * 33.33 / (time_step_minutes / 60)

                        # Calculate production load
                        production_load_kw = active_charge * production_efficiency / (time_step_minutes / 60)

                        # Total load for this bus
                        total_load_kw = dispensing_load_kw + production_load_kw
                        load_data[bus.bus_id] = total_load_kw

                        pump_next_available_time[i] = ts + timedelta(minutes=delta_time)

                        if bus.state_of_fuel < bus.fuel_capacity:
                            refuel_queue.append(bus)

            # Calculate total load as the sum of individual loads
            load_data['Total_Load'] = sum(load_data[bus.bus_id] for bus in buses)
            day_data.append(load_data)

        simulation_data.extend(day_data)

    simulation_df = pd.DataFrame(simulation_data)
    simulation_df.set_index('timestamp', inplace=True)

    # New Dataframe for Conversion Efficiency Plot
    efficiency_data = []
    for _, row in simulation_df.iterrows():
        total_load = row['Total_Load']
        electrolysis_load = total_load * 0.7
        tsd_load = electrolysis_load * 0.8
        fuel_cell_load = tsd_load * 0.55
        efficiency_data.append({
            'timestamp': row.name,
            'Electrolysis': electrolysis_load,
            'TSD': tsd_load,
            'Fuel_Cell': fuel_cell_load
        })

    efficiency_df = pd.DataFrame(efficiency_data)
    efficiency_df.set_index('timestamp', inplace=True)

    if output_path:
        simulation_df.to_csv(output_path)

    return simulation_df, efficiency_df
