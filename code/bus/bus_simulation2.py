import numpy as np
import pandas as pd
from datetime import timedelta, datetime
import os

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


def run_hydrogen_bus_simulation(params, output_path=None):
    """
    Runs a simulation for a fleet of hydrogen buses, calculating daily driving and refueling.

    Parameters:
    - params (dict): Dictionary of simulation parameters:
        - 'num_buses' (int): Number of buses in the fleet.
        - 'trips_per_day' (int): Total trips the fleet will complete each day.
        - 'kms_per_trip' (int): Distance for each trip in kilometers.
        - 'energy_per_km' (tuple): Energy per km in kWh (mean, std deviation).
        - 'fuel_capacity' (float): Maximum fuel capacity per bus in kg of H2.
        - 'flow_rate' (float): Refueling flow rate in kg/min.
        - 'pumps_available' (int): Number of hydrogen pumps available for refueling.
        - 'time_step' (int): Time step for the simulation in minutes.
        - 'deltaArrivalTime' (int): Gap between pump usage multiples (1=15min, 2=30min, etc.).
        - 'first_departure' (time): The earliest departure time for trips.
        - 'last_arrival' (time): The latest arrival time for trips.
        - 'start_date' (date): Start date of the simulation.
        - 'days_to_predict' (int): Number of days the simulation will run.
        - 'saturday_buses' (int): Number of buses on Saturday.
        - 'saturday_trips' (int): Number of trips on Saturday.

    Here is an example of a params dictionary:

    params = {
    'num_buses': 10,
    'trips_per_day': 80,
    'kms_per_trip': 10,
    'energy_per_km': (1.5, 0.3),  # average and standard deviation in kWh
    'fuel_capacity': 50,  # kg of H2
    'flow_rate': 4.5,  # kg/min
    'pumps_available': 2,
    'time_step': 15,  # minutes
    'deltaArrivalTime': 2,  # 2 * 15 minutes gap between pump usage
    'first_departure': datetime.strptime("06:00", "%H:%M").time(),
    'last_arrival': datetime.strptime("22:00", "%H:%M").time(),
    'start_date': datetime.today(),
    'days_to_predict': 7,
    'saturday_buses': 5,
    'saturday_trips': 40
    }

    Returns:
    - simulation_df (DataFrame): Simulation data for all buses and total load.
    - Optionally saves to CSV if output_path is specified.
    """

    time_step = pd.Timedelta(minutes=params['time_step'])
    time_step_minutes = params['time_step']
    delta_time = params['deltaArrivalTime'] * time_step_minutes  # Gap in minutes between each bus's charging session
    simulation_data = []

    # Iterate through each day
    for day in pd.date_range(start=params['start_date'], periods=params['days_to_predict']):
        if day.weekday() == 6:  # No buses run on Sundays
            continue
        elif day.weekday() == 5:  # Reduced fleet on Saturdays
            num_buses = params['saturday_buses']
            trips_per_day = params['saturday_trips']
        else:
            num_buses = params['num_buses']
            trips_per_day = params['trips_per_day']

        # Calculate trips per bus and distribute any remainder
        base_trips = trips_per_day // num_buses
        extra_trips = trips_per_day % num_buses

        # Initialize buses for the day
        buses = []
        for i in range(num_buses):
            trips_per_bus = base_trips + (1 if i < extra_trips else 0)
            bus = HydrogenBus(
                bus_id=f'Bus_{i+1}',
                trips_per_bus=trips_per_bus,
                kms_per_trip=params['kms_per_trip'],
                energy_per_km=params['energy_per_km'],
                fuel_capacity=params['fuel_capacity'],
                flow_rate=params['flow_rate']
            )
            buses.append(bus)

        pumps_available = params['pumps_available']
        day_data = []

        # Set charging window from last_arrival + 1 hour to next day's first_departure
        charging_start_time = datetime.combine(day, params['last_arrival']) + timedelta(hours=1)
        charging_end_time = datetime.combine(day + timedelta(days=1), params['first_departure'])

        # Generate a time series for the charging window, which can extend over midnight
        charging_time_series = pd.date_range(
            start=charging_start_time,
            end=charging_end_time,
            freq=time_step
        )

        # Queue to manage refueling
        refuel_queue = []
        for bus in buses:
            bus.simulate_day_driving()
            if bus.state_of_fuel < bus.fuel_capacity:
                bus.next_available_time = charging_start_time  # Set initial available time for charging
                refuel_queue.append(bus)

        # Track next available time for each pump to enforce the gap
        pump_next_available_time = [charging_start_time for _ in range(pumps_available)]

        # Iterate through each time step of the charging window, setting zero load where needed
        for ts in charging_time_series:
            load_data = {'timestamp': ts}
            total_load = 0

            # Initialize all buses with zero load for this time step (during driving hours or idle)
            for bus in buses:
                load_data[bus.bus_id] = 0

            # Check each pump for availability
            for i in range(pumps_available):
                if pump_next_available_time[i] <= ts and refuel_queue:
                    # Get the next bus in line that is eligible to use the pump
                    bus = refuel_queue.pop(0)
                    active_load = bus.incremental_charge(time_step_minutes)
                    load_kw = active_load * 33.33 / (time_step_minutes / 60)  # Convert kg of H2 to kW

                    load_data[bus.bus_id] = load_kw
                    total_load += load_kw

                    # Update the next available time for this pump to enforce the delay
                    pump_next_available_time[i] = ts + timedelta(minutes=delta_time)

                    # If the bus is not fully charged, add it back to the queue to continue in the next time step
                    if bus.state_of_fuel < bus.fuel_capacity:
                        refuel_queue.append(bus)

            load_data['Total_Load'] = total_load
            day_data.append(load_data)

        simulation_data.extend(day_data)

    # Convert to DataFrame
    simulation_df = pd.DataFrame(simulation_data)
    simulation_df.set_index('timestamp', inplace=True)

    if output_path:
        simulation_df.to_csv(output_path)
    return simulation_df
