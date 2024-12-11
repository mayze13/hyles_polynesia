import os
import sys
import pandas as pd
from tqdm import tqdm

# Work distribution percentages
work_distribution = {
    'Tipaerui': 0.15,
    'Vairaatoa': 0.60,
    'Arue': 0.02,
    'Papenoo Aval': 0.02,
    'Taravao': 0.05,
    'Atimaono': 0.01,
    'Punaruu': 0.15
}

def redistribute_loads(scenario_name):
    scenario_dir = f"./outputs/{scenario_name}"
    redist_dir = os.path.join(scenario_dir, "redistributed")
    os.makedirs(redist_dir, exist_ok=True)

    # Find all location load files
    location_files = [f for f in os.listdir(scenario_dir) if f.endswith("_location_load.csv")]
    dataframes = []

    with tqdm(total=len(location_files), desc=f"Reading location files for {scenario_name}") as pbar:
        for file in location_files:
            df = pd.read_csv(os.path.join(scenario_dir, file))
            # Check required columns
            if 'Work_Load' not in df.columns or 'Home_Load' not in df.columns:
                pbar.update(1)
                continue

            dataframes.append((file, df))
            pbar.update(1)

    if not dataframes:
        print(f"No valid location load files found for scenario {scenario_name}. Skipping redistribution.")
        return

    # Compute total sum of all Work_Load series
    total_work_sum = 0.0
    work_sums = []
    for (fname, df) in dataframes:
        w_sum = df['Work_Load'].sum()
        work_sums.append(w_sum)
        total_work_sum += w_sum

    # Redistribute loads
    with tqdm(total=len(dataframes), desc=f"Redistributing Work_Load for {scenario_name}") as pbar:
        for (fname, df), w_val in zip(dataframes, work_sums):
            base_name = fname.replace(f"_{scenario_name}_location_load.csv", "")
            poste_source = base_name.replace("_", " ")

            if poste_source not in work_distribution:
                # If no distribution specified, just copy as is
                df.to_csv(os.path.join(redist_dir, f"{base_name}_{scenario_name}_redist.csv"), index=False)
                pbar.update(1)
                continue

            target_fraction = work_distribution[poste_source]
            target_work = total_work_sum * target_fraction
            scaling_factor = target_work / w_val if w_val != 0 else 0.0
            df_redistributed = df.copy()
            df_redistributed['Work_Load'] = df_redistributed['Work_Load'] * scaling_factor
            df_redistributed.to_csv(os.path.join(redist_dir, f"{base_name}_{scenario_name}_redist.csv"), index=False)
            pbar.update(1)

    print(f"Redistribution completed for scenario: {scenario_name}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python redistribute_work.py <scenario_name>")
        sys.exit(1)

    scenario_name = sys.argv[1]
    redistribute_loads(scenario_name)
