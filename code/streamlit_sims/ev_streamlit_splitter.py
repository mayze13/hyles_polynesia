import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io
import numpy as np

# Configure page
st.set_page_config(page_title='EV Fleet Substation Redistribution', layout='wide')

# Title
st.title('Substation Redistribution of Work Load for EV Fleet')

# Session state for storing dataframes
if 'redistributed_dataframes' not in st.session_state:
    st.session_state.redistributed_dataframes = []
if 'original_dataframes' not in st.session_state:
    st.session_state.original_dataframes = []
if 'uploaded_file_names' not in st.session_state:
    st.session_state.uploaded_file_names = []

# File uploader to upload multiple CSV files
uploaded_files = st.file_uploader(
    "Upload Location Load CSV files for Work Redistribution",
    type=['csv'],
    accept_multiple_files=True
)

# Input redistribution percentages
if uploaded_files:
    st.sidebar.header('Redistribution Percentages for Each Substation')

    # Dynamic input of percentages for each substation based on the number of uploaded files
    redistribution_percentages = []
    uploaded_file_names = [uploaded_file.name for uploaded_file in uploaded_files]
    st.session_state.uploaded_file_names = uploaded_file_names  # Store the file names in session state

    for i, file_name in enumerate(uploaded_file_names):
        redistribution_percentages.append(
            st.sidebar.slider(f'{file_name} Redistribution %', min_value=0, max_value=100, value=0, step=1)
        )

    # Ensure that the sum of percentages is 100
    if sum(redistribution_percentages) != 100:
        st.warning("The sum of all redistribution percentages must equal 100%. Please adjust.")
    else:
        st.success("Redistribution percentages are correctly assigned.")

    # Process files if percentages are correctly assigned
    if st.button('Redistribute Load'):
        if sum(redistribution_percentages) != 100:
            st.error("Please make sure that the sum of redistribution percentages is 100%.")
        else:
            try:
                # Step 1: Resample and collect the Work_Load columns from all uploaded CSVs
                individual_dataframes = []

                # Read and process each uploaded CSV
                for uploaded_file in uploaded_files:
                    try:
                        # Read each uploaded CSV
                        content = uploaded_file.getvalue().decode('utf-8')  # Convert bytes to string
                        df = pd.read_csv(io.StringIO(content))

                        # Ensure required columns exist
                        if 'timestamp' not in df.columns or 'Work_Load' not in df.columns or 'Home_Load' not in df.columns:
                            st.error(f"Uploaded CSV '{uploaded_file.name}' is missing required columns ('timestamp', 'Work_Load', 'Home_Load'). Please upload a valid file.")
                            continue

                        # Convert timestamp to datetime and set as index
                        df['timestamp'] = pd.to_datetime(df['timestamp'])
                        df.set_index('timestamp', inplace=True)

                        # Resample to 1H intervals to align all dataframes
                        df_resampled = df.resample('1H').interpolate(method='linear')  # Interpolating to fill any gaps

                        # Append individual dataframes for future use
                        individual_dataframes.append(df_resampled)

                    except pd.errors.EmptyDataError:
                        st.error(f"Uploaded CSV '{uploaded_file.name}' appears to be empty or has no readable content.")
                        continue

                if not individual_dataframes:
                    st.error("No valid CSV files found. Please upload files with the required format.")
                else:
                    # Step 2: Calculate the total original AUC (area under the curve) for all substations
                    original_total_auc = sum(np.trapz(df['Work_Load'], x=df.index.astype(int)) for df in individual_dataframes)

                    # Calculate each substation's AUC for Work_Load and determine each substation's AUC share
                    original_aucs = [np.trapz(df['Work_Load'], x=df.index.astype(int)) for df in individual_dataframes]
                    original_shares = [auc / original_total_auc for auc in original_aucs]

                    # Create redistributed dataframes based on desired redistribution percentages
                    redistributed_dataframes = []
                    for idx, (percentage, df, original_share) in enumerate(zip(redistribution_percentages, individual_dataframes, original_shares)):
                        # Calculate the target AUC for this substation based on the redistribution percentage
                        target_auc = original_total_auc * (percentage / 100.0)

                        # Scaling factor to achieve the target AUC while preserving curve shape
                        scaling_factor = target_auc / original_aucs[idx]

                        # Adjust the Work_Load to match the target AUC
                        substation_df = df.copy()
                        substation_df['Work_Load'] *= scaling_factor
                        redistributed_dataframes.append(substation_df)

                    # Save redistributed dataframes to session state to persist after button press
                    st.session_state.redistributed_dataframes = redistributed_dataframes
                    st.session_state.original_dataframes = individual_dataframes

                    # Plot the original loads for comparison
                    fig_original = go.Figure()
                    for idx, substation_df in enumerate(individual_dataframes):
                        file_name = uploaded_file_names[idx]
                        fig_original.add_trace(go.Scatter(
                            x=substation_df.index,
                            y=substation_df['Work_Load'],
                            mode='lines',
                            name=f'Original {file_name} Work Load',
                            line=dict(width=2)
                        ))
                        fig_original.add_trace(go.Scatter(
                            x=substation_df.index,
                            y=substation_df['Home_Load'],
                            mode='lines',
                            name=f'Original {file_name} Home Load',
                            line=dict(width=2),
                            visible='legendonly'  # Default visibility is off
                        ))

                    fig_original.update_layout(
                        title='Original Work Load for Each Substation',
                        xaxis_title='Time',
                        yaxis_title='Power Demand (kW)',
                        hovermode='x unified',
                        xaxis=dict(tickformat='%b %d, %H:%M'),
                        yaxis=dict(ticksuffix=' kW')
                    )
                    st.plotly_chart(fig_original, use_container_width=True)

                    # Plot the redistributed loads
                    fig = go.Figure()
                    for idx, substation_df in enumerate(redistributed_dataframes):
                        file_name = uploaded_file_names[idx]
                        fig.add_trace(go.Scatter(
                            x=substation_df.index,
                            y=substation_df['Work_Load'],
                            mode='lines',
                            name=f'Redistributed {file_name} Work Load',
                            line=dict(width=2)
                        ))
                        fig.add_trace(go.Scatter(
                            x=substation_df.index,
                            y=substation_df['Home_Load'],
                            mode='lines',
                            name=f'Redistributed {file_name} Home Load',
                            line=dict(width=2),
                            visible='legendonly'  # Default visibility is off
                        ))

                    fig.update_layout(
                        title='Redistributed Work Load for Each Substation',
                        xaxis_title='Time',
                        yaxis_title='Power Demand (kW)',
                        hovermode='x unified',
                        xaxis=dict(tickformat='%b %d, %H:%M'),
                        yaxis=dict(ticksuffix=' kW')
                    )
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"An error occurred during the redistribution process: {str(e)}")

# Allow download of updated CSV files without re-running the simulation
if st.session_state.redistributed_dataframes:
    st.subheader("Download Redistributed CSV Files")

    for idx, substation_df in enumerate(st.session_state.redistributed_dataframes):
        csv_buffer = io.StringIO()
        substation_df.reset_index().to_csv(csv_buffer, index=False)
        file_name = st.session_state.uploaded_file_names[idx]
        st.download_button(
            label=f"Download Updated CSV for {file_name}",
            data=csv_buffer.getvalue(),
            file_name=f"{file_name}_redistributed_load.csv",
            mime='text/csv'
        )
