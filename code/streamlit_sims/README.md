# Electric Vehicle Fleet Simulation

This repository contains a simulation of an electric vehicle (EV) fleet, including a command-line interface (CLI) and an interactive web-based user interface built using Streamlit. The purpose of this simulation is to understand the charging load, energy consumption, and redistribution of the EV fleet across different locations under varying conditions.

## Contents

- `ev_fleet_simulation.py`: Backend Python script that contains the main logic for simulating the fleet's energy usage and charging behavior.
- `ev_streamlit.py`: Streamlit app for running the EV fleet simulation with an interactive interface.
- `ev_streamlit_splitter.py`: Streamlit app for work-load redistribution among substations.
- `requirements.txt`: Dependencies required to run the project.

## Getting Started

To use this project, you can choose to run the simulation either via the command line using `ev_fleet_simulation.py` or interactively using the Streamlit web interface (`ev_streamlit.py`). For load redistribution scenarios, you can use `ev_streamlit_splitter.py`.

### Prerequisites

- Python 3.7 or higher
- [Streamlit](https://streamlit.io/) for the interactive web-based interface

Install the necessary Python packages with the following command:

```sh
pip install -r requirements.txt
```

## Graphical User Interface Usage (Streamlit)

The Streamlit interface provides an interactive way to configure the parameters and visualize the results of the EV fleet simulation.

### Running the Streamlit Application

To run the simulation via Streamlit, use the following command:

```sh
streamlit run ev_streamlit.py
```

### Application Interface Overview

When you run the application, you will see the following options:

- **Simulation Name**: Give your simulation a unique name for easy identification.
- **Simulation Parameters**: Set the number of simulation days, start date, and time resolution for simulation results.
- **Fleet Parameters**: Adjust the number of each type of vehicle in the fleet, including BEVs, PHEVs, LDVs, and two-wheelers.
- **Average Daily Distance**: Set the average daily distances for weekdays and weekends along with their respective standard deviations.
- **Randomness Parameter**: Introduces a variability factor into the simulation for more realistic results.
- **Vehicle Type Parameters**: Configure battery capacity and energy consumption rates for each vehicle type.

Click **Run Simulation** to initiate the simulation. Results are displayed as time-series plots of the charging load over time, split by vehicle type and location.

### Output Files
- **CSV File**: Contains detailed load profiles, including the charging events for each vehicle type, the total load over time, and the location load profiles (Home and Work).

### Parameter Walkthrough in Streamlit
- **Simulation Name**: Name of the current simulation to keep track of multiple runs.
- **Simulation Days**: Number of days for which the simulation will be run.
- **Time Step**: Defines the granularity of the simulation output (e.g., 10 minutes, 30 minutes, or hourly).
- **Work Charging Probability**: Probability that vehicles will charge at work, as a percentage.
- **Fleet Composition**: Number of BEVs, PHEVs, LDVs, and two-wheelers in the fleet.
- **Daily Distance (Weekday and Weekend)**: Mean and standard deviation for distances covered during weekdays and weekends.
- **Battery and Energy Parameters**: Define the battery capacity and energy consumption (in kWh/km) for each type of vehicle.

## Substation Redistribution Tool (Streamlit)

The load redistribution tool (`ev_streamlit_splitter.py`) allows you to redistribute work-based EV charging loads across substations.

### Running the Substation Redistribution App

To redistribute load, use the following command:

```sh
streamlit run ev_streamlit_splitter.py
```

### Application Interface Overview

- **Upload Location Load CSV Files**: Upload CSV files containing location load data, which are generated from the main fleet simulation.
- **Redistribution Percentages**: Set how the work-based charging loads are distributed across multiple substations. Ensure that the total percentage equals 100%.
- **Redistribute Load Button**: Redistribute the loads based on your input percentages.
- **Download Updated CSV**: Download the new CSV files containing redistributed load profiles for each substation.

### Input Requirements

- **Location Load CSV**: Must include columns for `timestamp`, `Work_Load`, and `Home_Load`.
- **Redistribution Percentages**: Ensure that the total of all percentages adds up to 100%, which is a requirement for load balancing.

## Example Usage Scenarios
- **Fleet Managers**: Assess the charging behavior and energy demand of different vehicle types under varying conditions.
- **Energy Providers**: Understand the impact of EV charging loads on grid substations, and efficiently redistribute work-based charging to balance demand.
- **Researchers**: Investigate the interplay between different types of electric vehicles and their charging behavior in various scenarios.

## Contributing
If you wish to contribute to this project, feel free to fork it, make modifications, and create pull requests. Contributions are welcome.

## License
This project is licensed under the MIT License. See `LICENSE` for more details.

## Contact
For more information or support, please contact [james.moultrie13@gmail.com].
