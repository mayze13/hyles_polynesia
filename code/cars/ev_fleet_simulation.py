import numpy as np
import pandas as pd
from datetime import timedelta, datetime
import random
import math

class Vehicle:
    def __init__(self, vehicle_id, vehicle_type, battery_capacity, energy_consumption,
                 daily_distance_weekday, daily_distance_weekend, charging_behavior,
                 home_departure_time, home_departure_std, work_departure_time, work_departure_std):
        self.vehicle_id = vehicle_id
        self.vehicle_type = vehicle_type
        self.battery_capacity = battery_capacity
        self.energy_consumption = energy_consumption
        self.daily_distance_weekday = daily_distance_weekday
        self.daily_distance_weekend = daily_distance_weekend
        self.charging_behavior = charging_behavior
        self.state_of_charge = np.random.uniform(0.4, 0.6) * battery_capacity
        self.home_departure_time = home_departure_time
        self.home_departure_std = home_departure_std
        self.work_departure_time = work_departure_time
        self.work_departure_std = work_departure_std

    def get_temperature_adjustment(self, current_date):
        month = current_date.month
        if month in [12, 1, 2, 3]:  # Winter months
            return 1.15  # 15% increase
        elif month in [6, 7]:  # Summer months
            return 0.85  # 15% decrease
        return 1.0  # No change

    def drive(self, day_type, current_date):
        # Select daily distance based on day type
        daily_distance = self.daily_distance_weekday if day_type == 'Weekday' else self.daily_distance_weekend
        distance = max(0, np.random.normal(*daily_distance))
        adjustment_factor = self.get_temperature_adjustment(current_date)
        energy_used = distance * self.energy_consumption * adjustment_factor
        self.state_of_charge = max(self.state_of_charge - energy_used, 0)

    def determine_arrival_departure_times(self, behavior, day_type, current_date):
        if behavior['location'] == 'Home':
            mean_arrival_hour = 17.5 if day_type == 'Weekday' else 16.0
            std_deviation = 1.5 if day_type == 'Weekday' else 3.0
        else:  # Work location
            mean_arrival_hour = 7.5
            std_deviation = 1.5
        skew_factor = 2 if random.random() > 0.5 else -1
        arrival_time = current_date + timedelta(hours=np.random.normal(mean_arrival_hour, std_deviation) + skew_factor)
        departure_time = (current_date + timedelta(days=1)).replace(
            hour=self.home_departure_time.hour if behavior['location'] == 'Home' else self.work_departure_time.hour,
            minute=0
        ) + timedelta(hours=np.random.normal(0, self.home_departure_std if behavior['location'] == 'Home' else self.work_departure_std))

        if day_type == 'Weekend' and behavior['location'] == 'Home':
            departure_time += timedelta(hours=np.random.uniform(0, 2))

        return arrival_time, departure_time

    def charge(self, current_date, randomness=0.1, work_charging_probability=0.5):
        charging_events = []
        day_type = 'Weekend' if current_date.weekday() >= 5 else 'Weekday'

        for behavior in self.charging_behavior:
            # Determine if vehicle will charge at the workplace
            if behavior['location'] == 'Work' and ((day_type == 'Weekday' and random.random() > work_charging_probability) or
                                                   (day_type == 'Weekend' and random.random() > work_charging_probability / 3)):
                continue

            arrival_time, departure_time = self.determine_arrival_departure_times(behavior, day_type, current_date)

            # Add variability to charging times
            charging_start_delay = np.random.uniform(-1.5, 2.0) if day_type == 'Weekend' else np.random.uniform(-1.5, 1.5)
            start_time = arrival_time + timedelta(hours=charging_start_delay)
            charging_power = behavior['power']

            # Calculate charging duration based on power and SOC
            end_time = min(departure_time, start_time + timedelta(hours=(self.battery_capacity - self.state_of_charge) / charging_power))

            # SOC-based charging behavior
            should_charge = (
                self.state_of_charge < 0.2 * self.battery_capacity or
                (self.state_of_charge > 0.7 * self.battery_capacity and random.random() < 0.3) or
                (0.2 * self.battery_capacity <= self.state_of_charge <= 0.7 * self.battery_capacity)
            )

            if should_charge:
                charging_events.extend(self._generate_charging_events(start_time, end_time, behavior, randomness))

            # Add midday or evening charging events at work
            if behavior['location'] == 'Work' and day_type == 'Weekday':
                if random.random() < 0.02:  # Midday charging
                    midday_start = current_date.replace(hour=11, minute=30) + timedelta(hours=np.random.normal(0, 0.5))
                    midday_end = midday_start + timedelta(hours=2)
                    charging_events.extend(self._generate_charging_events(midday_start, midday_end, behavior, randomness))
                if random.random() < 0.01:  # Evening charging
                    evening_start = current_date.replace(hour=13, minute=30) + timedelta(hours=np.random.normal(0, 1))
                    evening_end = min(current_date.replace(hour=20, minute=0), evening_start + timedelta(hours=1.5))
                    charging_events.extend(self._generate_charging_events(evening_start, evening_end, behavior, randomness))

        return charging_events

    def _generate_charging_events(self, start_time, end_time, behavior, randomness):
        charging_events = []
        charging_duration = (end_time - start_time).total_seconds() / 3600
        charging_power = behavior['power'] * (1 + np.random.uniform(-0.1, 0.1) * randomness)
        energy_transferred = min(self.battery_capacity - self.state_of_charge, charging_power * charging_duration)
        self.state_of_charge += energy_transferred

        time_steps = pd.date_range(start=start_time, end=end_time, freq='10min')
        for t in time_steps:
            power_variation = charging_power * (1 + np.random.uniform(-0.1, 0.1) * randomness)
            charging_events.append({
                'vehicle_id': self.vehicle_id,
                'timestamp': t,
                'power': power_variation,  # Power in kW
                'vehicle_type': self.vehicle_type,
                'location': behavior['location']
            })

        return charging_events

# Simulation function (unchanged structure but more readable)

def run_simulation(params, progress_callback=None):
    fleet = []
    vehicle_types = ['EV', 'PHEV', 'LDV', 'Two Wheeler']
    vehicle_params = ['ev_params', 'phev_params', 'ldv_params', 'two_wheeler_params']
    num_vehicles = ['num_evs', 'num_phevs', 'num_ldvs', 'num_two_wheelers']

    for v_type, param_key, num_key in zip(vehicle_types, vehicle_params, num_vehicles):
        for i in range(params[num_key]):
            fleet.append(Vehicle(
                vehicle_id=f'{v_type}_{i+1}',
                vehicle_type=v_type,
                battery_capacity=params[param_key]['battery_capacity'],
                energy_consumption=params[param_key]['energy_consumption'],
                daily_distance_weekday=params['daily_distance_weekday'],
                daily_distance_weekend=params['daily_distance_weekend'],
                charging_behavior=[
                    {'location': 'Home', 'power': 7.4, 'strategy': 'Immediate'},
                    {'location': 'Work', 'power': 11, 'strategy': 'Delayed'}
                ],
                home_departure_time=params['home_departure_time'],
                home_departure_std=params['home_departure_std'],
                work_departure_time=params['work_departure_time'],
                work_departure_std=params['work_departure_std']
            ))

    # Stabilization phase
    stabilization_range = pd.date_range(start=params['start_date'] - timedelta(days=3), periods=3, freq='D')
    for current_date in stabilization_range:
        day_type = 'Weekend' if current_date.weekday() >= 5 else 'Weekday'
        for vehicle in fleet:
            vehicle.drive(day_type, current_date)
            vehicle.charge(current_date, randomness=params.get('randomness', 0.1), work_charging_probability=params['work_charging_probability'])

    # Main simulation
    charging_events_list = []
    total_steps = len(params['date_range']) * len(fleet)
    current_step = 0

    for current_date in params['date_range']:
        day_type = 'Weekend' if current_date.weekday() >= 5 else 'Weekday'
        for vehicle in fleet:
            vehicle.drive(day_type, current_date)
            charging_events = vehicle.charge(current_date, randomness=params.get('randomness', 0.1), work_charging_probability=params['work_charging_probability'])
            charging_events_list.extend(charging_events)
            current_step += 1
            if progress_callback:
                progress_callback(current_step / total_steps)

    # Data processing for load profiles
    charging_events_df = pd.DataFrame(charging_events_list)
    if charging_events_df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    charging_events_df['timestamp'] = pd.to_datetime(charging_events_df['timestamp'])
    charging_events_df.set_index('timestamp', inplace=True)

    # Generate load profiles by vehicle type
    vehicle_types_dict = {'EV': 'BEV_Load', 'PHEV': 'PHEV_Load', 'LDV': 'LDV_Load', 'Two Wheeler': 'Two_Wheeler_Load'}

    # Time step in hours (e.g., for 10 minutes, it's 10/60 = 0.1667 hours)
    time_step_hours = pd.to_timedelta(params['resample_time']).total_seconds() / 3600.0

    load_profile = pd.concat(
        [
            (charging_events_df[charging_events_df['vehicle_type'] == v_type]['power']
            .resample(params['resample_time'])
            .sum()
            .div(time_step_hours)  # Convert total energy (kWh) to average power (kW)
            .rename(load_name))
            for v_type, load_name in vehicle_types_dict.items()
        ],
        axis=1
    ).fillna(0)

    load_profile['Total_Load'] = load_profile.sum(axis=1)

    # Load profiles by location
    location_profile = pd.concat([
        (charging_events_df[charging_events_df['location'] == loc]['power']
        .resample(params['resample_time'])
        .sum()
        .div(time_step_hours)  # Convert total energy (kWh) to average power (kW)
        .rename(f"{loc}_Load"))
        for loc in ['Home', 'Work']
    ], axis=1).fillna(0)
    location_profile['Total_Load'] = location_profile.sum(axis=1)

    return charging_events_df.reset_index(), load_profile, location_profile
