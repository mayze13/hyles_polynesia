import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, time
from tqdm import tqdm
from ev_fleet_simulation import run_simulation

if len(sys.argv) < 2:
    print("Usage: python run_all_scenarios.py <run_name>")
    sys.exit(1)

run_name = sys.argv[1]

# Updated Vehicle Parameters
ev_battery_capacity = 50.0
ev_energy_consumption = 0.15
phev_battery_capacity = 12.0
phev_energy_consumption = 0.20
ldv_battery_capacity = 60.0
ldv_energy_consumption = 0.20
two_wheeler_battery_capacity = 2.5
two_wheeler_energy_consumption = 0.025

# Updated Daily Distances per Poste Source
distance_data = {
    'Tipaerui': {
        'weekday': (20, 5),
        'weekend': (30, 10)
    },
    'Vairaatoa': {
        'weekday': (15, 5),
        'weekend': (30, 10)
    },
    'Arue': {
        'weekday': (20, 5),
        'weekend': (30, 10)
    },
    'Papenoo Aval': {
        'weekday': (50, 10),
        'weekend': (30, 15)
    },
    'Taravao': {
        'weekday': (60, 20),
        'weekend': (30, 20)
    },
    'Atimaono': {
        'weekday': (50, 20),
        'weekend': (30, 20)
    },
    'Punaruu': {
        'weekday': (30, 10),
        'weekend': (30, 15)
    }
}

# Scenario Data
scenario_data = {
    'low': {
        'Tipaerui':    {'BEV': 393,  'PHEV': 752,  'LDV': 239, 'Two_Wheeler': 171},
        'Vairaatoa':   {'BEV': 437,  'PHEV': 835,  'LDV': 265, 'Two_Wheeler': 189},
        'Arue':        {'BEV': 108,  'PHEV': 207,  'LDV': 66,  'Two_Wheeler': 47},
        'Papenoo Aval':{'BEV': 174,  'PHEV': 333,  'LDV':106,  'Two_Wheeler':76},
        'Taravao':     {'BEV': 104,  'PHEV': 198,  'LDV':63,   'Two_Wheeler':45},
        'Atimaono':    {'BEV': 207,  'PHEV': 395,  'LDV':126,  'Two_Wheeler':90},
        'Punaruu':     {'BEV': 555,  'PHEV':1062,  'LDV':338,  'Two_Wheeler':241}
    },
    'mid': {
        'Tipaerui':    {'BEV':746,  'PHEV':1426, 'LDV':454, 'Two_Wheeler':324},
        'Vairaatoa':   {'BEV':827,  'PHEV':1582, 'LDV':504, 'Two_Wheeler':359},
        'Arue':        {'BEV':108,  'PHEV':207,  'LDV':66,  'Two_Wheeler':47},
        'Papenoo Aval':{'BEV':330,  'PHEV':631,  'LDV':201, 'Two_Wheeler':144},
        'Taravao':     {'BEV':195,  'PHEV':374,  'LDV':119, 'Two_Wheeler':85},
        'Atimaono':    {'BEV':392,  'PHEV':748,  'LDV':238, 'Two_Wheeler':170},
        'Punaruu':     {'BEV':1054, 'PHEV':2016, 'LDV':642, 'Two_Wheeler':458}
    },
    'high': {
        'Tipaerui':    {'BEV':1260, 'PHEV':2410, 'LDV':767,  'Two_Wheeler':548},
        'Vairaatoa':   {'BEV':1398, 'PHEV':2675, 'LDV':851,  'Two_Wheeler':607},
        'Arue':        {'BEV':108,  'PHEV':207,  'LDV':66,   'Two_Wheeler':47},
        'Papenoo Aval':{'BEV':558,  'PHEV':1067, 'LDV':339,  'Two_Wheeler':243},
        'Taravao':     {'BEV':330,  'PHEV':633,  'LDV':201,  'Two_Wheeler':144},
        'Atimaono':    {'BEV':662,  'PHEV':1266, 'LDV':402,  'Two_Wheeler':288},
        'Punaruu':     {'BEV':1781, 'PHEV':3407, 'LDV':1084, 'Two_Wheeler':775}
    }
}

work_distribution = {
    'Tipaerui': 0.15,
    'Vairaatoa': 0.60,
    'Arue': 0.02,
    'Papenoo Aval': 0.02,
    'Taravao': 0.05,
    'Atimaono': 0.01,
    'Punaruu': 0.15
}

# Common Simulation Parameters
simulation_days = 365
resample_time = "10min"
start_date = pd.Timestamp(datetime.now().date())
work_charging_probability = 0.7
randomness = 0.1
home_departure_time = time(7,0)
home_departure_std = 0.5
work_departure_time = time(17,0)
work_departure_std = 0.5

base_output_dir = os.path.join("./outputs", run_name)
os.makedirs(base_output_dir, exist_ok=True)

def run_scenario(scenario_name, poste_source_name, vehicle_counts):
    weekday_dist = distance_data[poste_source_name]['weekday']
    weekend_dist = distance_data[poste_source_name]['weekend']

    params = {
        'simulation_days': simulation_days,
        'start_date': start_date,
        'num_evs': vehicle_counts['BEV'],
        'num_phevs': vehicle_counts['PHEV'],
        'num_ldvs': vehicle_counts['LDV'],
        'num_two_wheelers': vehicle_counts['Two_Wheeler'],

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

        'daily_distance_weekday': weekday_dist,
        'daily_distance_weekend': weekend_dist,

        'home_departure_time': home_departure_time,
        'home_departure_std': home_departure_std,
        'work_departure_time': work_departure_time,
        'work_departure_std': work_departure_std,
        'randomness': randomness,
        'date_range': pd.date_range(start=start_date, periods=simulation_days, freq='D'),
        'work_charging_probability': work_charging_probability,
        'resample_time': resample_time
    }

    charging_events_df, load_profile, location_profile = run_simulation(params)

    scenario_dir = os.path.join(base_output_dir, scenario_name)
    os.makedirs(scenario_dir, exist_ok=True)

    poste_source_filename = poste_source_name.replace(" ", "_")

    # Ensure timestamp column in load_profile
    if not load_profile.empty:
        load_profile.index.name = 'timestamp'
        load_profile = load_profile.sort_index().reset_index()
        load_profile.to_csv(os.path.join(scenario_dir, f"{poste_source_filename}_{scenario_name}_load.csv"), index=False)

    # Ensure timestamp column in location_profile
    if not location_profile.empty:
        location_profile.index.name = 'timestamp'
        location_profile = location_profile.sort_index().reset_index()
        if "Home_Load" not in location_profile.columns:
            location_profile["Home_Load"] = 0.0
        if "Work_Load" not in location_profile.columns:
            location_profile["Work_Load"] = 0.0
        location_profile.to_csv(os.path.join(scenario_dir, f"{poste_source_filename}_{scenario_name}_location_load.csv"), index=False)

    return True

def redistribute_loads(scenario_name, work_distribution):
    scenario_dir = os.path.join(base_output_dir, scenario_name)
    redist_dir = os.path.join(scenario_dir, "redistributed")
    os.makedirs(redist_dir, exist_ok=True)

    location_files = [f for f in os.listdir(scenario_dir) if f.endswith("_location_load.csv")]
    dataframes = []

    with tqdm(total=len(location_files), desc=f"Reading location files for {scenario_name}") as pbar:
        for file in location_files:
            df = pd.read_csv(os.path.join(scenario_dir, file))
            if 'timestamp' not in df.columns or 'Work_Load' not in df.columns or 'Home_Load' not in df.columns:
                pbar.update(1)
                continue

            # Convert timestamp to datetime and set index
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp').set_index('timestamp')
            dataframes.append((file, df))
            pbar.update(1)

    if not dataframes:
        print(f"No valid location load files found for scenario {scenario_name}. Skipping redistribution.")
        return

    # Compute total AUC directly from original data without resampling
    total_auc = 0.0
    aucs = []
    for (fname, df) in dataframes:
        x = df.index.view(np.int64)  # nanoseconds
        auc = np.trapz(df['Work_Load'], x=x)
        aucs.append(auc)
        total_auc += auc

    with tqdm(total=len(dataframes), desc=f"Redistributing Work_Load for {scenario_name}") as pbar:
        for (fname, df), auc_value in zip(dataframes, aucs):
            base_name = fname.replace(f"_{scenario_name}_location_load.csv", "")
            poste_source = base_name.replace("_", " ")

            df_redistributed = df.copy()
            if poste_source in work_distribution:
                target_fraction = work_distribution[poste_source]
                target_auc = total_auc * target_fraction
                scaling_factor = target_auc / auc_value if auc_value != 0 else 0.0
                df_redistributed['Work_Load'] *= scaling_factor

            # Add timestamp as column
            df_redistributed = df_redistributed.sort_index()
            df_redistributed['timestamp'] = df_redistributed.index
            df_redistributed = df_redistributed.reset_index(drop=True)
            df_redistributed.to_csv(os.path.join(redist_dir, f"{base_name}_{scenario_name}_redist.csv"), index=False)
            pbar.update(1)


all_scenarios = list(scenario_data.keys())
with tqdm(total=len(all_scenarios), desc="Overall Scenario Processing") as scenario_pbar:
    for scenario_name, locations_data in scenario_data.items():
        poste_sources = list(locations_data.keys())
        with tqdm(total=len(poste_sources), desc=f"Scenario: {scenario_name}") as poste_pbar:
            for poste_source_name, vehicle_counts in locations_data.items():
                run_scenario(scenario_name, poste_source_name, vehicle_counts)
                poste_pbar.update(1)
        redistribute_loads(scenario_name, work_distribution)
        scenario_pbar.update(1)

print("All scenarios completed.")
