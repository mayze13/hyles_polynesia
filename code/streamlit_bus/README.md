# Hydrogen Bus Fleet Simulation

This repository contains a simulation of a hydrogen-powered bus fleet, implemented with both a command-line interface (CLI) and an interactive web-based user interface built using Streamlit. The goal of this simulation is to provide insights into the fuel consumption and refueling schedule of a fleet of hydrogen-powered buses under various operational scenarios.

## Contents

- `bus_simulation.py`: Python script to run the hydrogen bus simulation in standalone mode via the command line.
- `bus_streamlit.py`: Streamlit app for interactive simulation with a graphical interface.
- `README.md`: This document, providing instructions on how to use both versions of the tool.
- `requirements.txt`: Required dependencies for running the Python scripts.

## Getting Started

To use this project, you can choose between running the simulation via the command line (`bus_simulation.py`) or using the graphical interface provided by Streamlit (`bus_streamlit.py`). Follow the instructions below to get started.

### Prerequisites

- Python 3.7 or higher
- [Streamlit](https://streamlit.io/) for the interactive interface

Install the necessary Python packages with the following command:

```sh
pip install -r requirements.txt
```

## Command Line Interface Usage (Standalone Mode)

The command-line version is provided in `bus_simulation.py`. This version allows you to run the simulation and output results to a CSV file as well as an HTML to visualise the time-series.

### Running the Simulation

The script accepts an input CSV or Excel file with the simulation parameters. The input file should be formatted with the following columns:

| num_buses | trips_per_day | kms_per_trip | energy_per_km | energy_std | fuel_capacity | flow_rate | pumps_available | time_step | deltaArrivalTime | first_departure | last_arrival | start_date | days_to_predict | saturday_buses | saturday_trips |
| ----------| --------------| -------------| --------------| -----------| --------------| ----------| ----------------| ----------| ----------------| ----------------| -------------| -----------| ---------------| --------------| -------------- |
| 10        | 80            | 16           | 1.5           | 0.3        | 50            | 1         | 2              | 15        | 2               | 06:00          | 22:00        | 2024-11-04 | 7             | 5              | 40             |

**Example Command:**

```sh
python bus_simulation.py example_data/Params.csv test
```

This command will:
- Read input parameters from `Params.csv`.
- Generate an output CSV file (`simulation_results.csv`) in the `./output/` directory.
- Generate an interactive HTML plot (`test.html`) of the load over time.

### Command-Line Parameters Explained

- **`example_data/Params.csv`**: Path to the input CSV or Excel file containing all required parameters.
- **`test`**: Name for the output files (CSV and HTML). These will be saved in the `./output/` directory.

### Input File Parameter Description
- **`num_buses`**: Number of buses operating during weekdays.
- **`trips_per_day`**: Total number of trips per day per bus during weekdays.
- **`kms_per_trip`**: Distance of each trip in kilometers.
- **`energy_per_km`**: Average energy consumption per kilometer (kWh).
- **`energy_std`**: Standard deviation of energy consumption per kilometer.
- **`fuel_capacity`**: Fuel capacity of each bus in kg of H2.
- **`flow_rate`**: Refueling flow rate in kg per minute.
- **`pumps_available`**: Number of hydrogen pumps available.
- **`time_step`**: Length of each time step for the simulation (minutes).
- **`deltaArrivalTime`**: Time gap (in multiples of time steps) between consecutive buses arriving for refueling.
- **`first_departure`**: Earliest departure time for buses.
- **`last_arrival`**: Latest arrival time for buses.
- **`start_date`**: Start date for the simulation.
- **`days_to_predict`**: Number of days to run the simulation.
- **`saturday_buses`**: Number of buses operating on Saturdays.
- **`saturday_trips`**: Number of trips per day on Saturdays.

## Graphical User Interface Usage (Streamlit)

The Streamlit interface provides an easy-to-use graphical environment where you can adjust simulation parameters interactively and visualize results instantly.

### Running the Streamlit Application

To run the Streamlit interface, use the following command:

```sh
streamlit run bus_streamlit.py
```

### Application Interface Overview

When you run the application, you will see the following options:

- **Upload Parameters File**: Upload a CSV or Excel file with the same format as described above to pre-load the parameters.
- **Manual Input**: Adjust the parameters directly in the Streamlit app. The same parameters as described in the CLI are presented for manual entry.
- **Run Simulation Button**: Once all parameters are set, click this button to execute the simulation.
- **Simulation Results**: After running the simulation, the resulting load distribution will be displayed both as a data table and as an interactive stacked area chart using Plotly.
- **Download Results**: You can download the simulation data as a CSV file.

### Parameter Walkthrough in Streamlit

- **Number of Buses (Weekdays)**: Number of buses operating on weekdays.
- **Trips per Day (Weekdays)**: Number of trips each bus takes during a weekday.
- **Kilometers per Trip**: Distance covered per trip.
- **Energy per km (kWh)**: Average energy consumption for each kilometer.
- **Energy Std (kWh)**: Standard deviation in energy consumption.
- **Fuel Capacity (kg of H2)**: Maximum fuel capacity for each bus.
- **Flow Rate (kg/min)**: Rate at which hydrogen fuel is supplied during refueling.
- **Pumps Available**: Number of hydrogen pumps available.
- **Time Step (minutes)**: Duration of each time interval in the simulation.
- **Gap Between Pump Usages**: Gap between two buses arriving at the pump (in time steps).
- **First Departure & Last Arrival**: Define the start and end times for bus services during the day.
- **Start Date & Days to Predict**: Define when the simulation should start and the duration of the simulation in days.
- **Saturday Parameters**: Define special operational parameters for Saturdays (number of buses and trips).

## Output Files
- **CSV File**: Contains a detailed log of the bus load over time for each bus as well as the total fleet load.
- **HTML File**: A Plotly-based interactive visualization of the load for each bus and total fleet load over time, which allows zooming and detailed inspection of trends.

## Example Usage Scenarios
- **Fleet Managers**: Assess the fuel and load dynamics of a hydrogen-powered fleet under different operational conditions.
- **Researchers**: Use this tool to study energy consumption variability and optimize refueling strategies.

## Contributing
If you have suggestions, bug reports, or feature requests, please feel free to create an issue or submit a pull request.

## License
This project is licensed under the MIT License. See `LICENSE` for more information.

## Contact
For further questions or support, please contact [james.moultrie13@gmail.com].

