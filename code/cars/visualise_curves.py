import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title='Multi-Curve EV Load Visualization', layout='wide')
st.title("Multi-Curve Load Visualization")

# Sidebar checkboxes for toggling visibility
show_home = st.sidebar.checkbox("Show Home Curves", value=True)
show_work = st.sidebar.checkbox("Show Work Curves", value=True)

uploaded_files = st.file_uploader("Upload CSV files", type=['csv'], accept_multiple_files=True)

if uploaded_files:
    fig = go.Figure()
    used_timestamp = False
    all_x_data = []

    for uploaded_file in uploaded_files:
        df = pd.read_csv(uploaded_file)

        if 'Home_Load' not in df.columns or 'Work_Load' not in df.columns:
            st.warning(f"Skipping {uploaded_file.name}: Missing 'Home_Load' or 'Work_Load' columns.")
            continue

        x_label = 'Index'
        x_data = df.index
        # Parse timestamp if available and valid
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            # If timestamp parsing succeeds and all not null
            if df['timestamp'].notnull().all():
                x_data = df['timestamp']
                used_timestamp = True
                x_label = 'Time'

        fig.add_trace(go.Scatter(
            x=x_data, y=df['Home_Load'],
            mode='lines', name=f"{uploaded_file.name} - Home_Load",
            visible='legendonly' if not show_home else True
        ))
        fig.add_trace(go.Scatter(
            x=x_data, y=df['Work_Load'],
            mode='lines', name=f"{uploaded_file.name} - Work_Load",
            visible='legendonly' if not show_work else True
        ))

    fig.update_layout(
        title="Combined Load Curves",
        xaxis_title=x_label,
        yaxis_title='Power (kW)',
        hovermode='x unified'
    )

    # Adjust visibility after creation
    for trace in fig.data:
        if "Home_Load" in trace.name:
            trace.visible = True if show_home else 'legendonly'
        elif "Work_Load" in trace.name:
            trace.visible = True if show_work else 'legendonly'

    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Please upload one or more CSV files to visualize the curves.")
