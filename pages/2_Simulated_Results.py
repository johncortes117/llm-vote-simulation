import streamlit as st
import pandas as pd
from core.data_processing import process_simulated_votes, aggregate_results_by_state
from core.plotting import plot_election_map_plotly

st.set_page_config(page_title="Simulated Results", page_icon="📊", layout="wide")

st.title("📊 Simulated Election Results")

# Load data from session state
if 'simulated_profiles_with_votes_df' not in st.session_state or st.session_state.simulated_profiles_with_votes_df is None:
    st.warning("No simulation data found. Please run a simulation on the '⚙️ Simulation Configuration' page first.")
    st.stop()

if 'aggregated_results_df' not in st.session_state or st.session_state.aggregated_results_df is None:
    # Process and aggregate if not already done (e.g., if user navigates directly after simulation)
    processed_df = process_simulated_votes(st.session_state.simulated_profiles_with_votes_df.copy())
    st.session_state.aggregated_results_df = aggregate_results_by_state(processed_df)

if 'us_states_gdf' not in st.session_state or st.session_state.us_states_gdf is None:
    st.error("US States GeoJSON data not loaded. Map cannot be displayed. Check app.py or main page.")
    st.stop()

# --- Display Aggregated Results ---
st.header("State-Level Aggregated Results")
if st.session_state.aggregated_results_df.empty:
    st.warning("Aggregated results are empty. This might happen if the simulation produced no valid votes or if there was an issue in processing.")
else:
    st.dataframe(st.session_state.aggregated_results_df)

    # --- Election Map Visualization ---
    st.header("Simulated Election Map")
    
    # Define color map for winners
    color_map = {
        "Democrat": "blue",
        "Republican": "red",
        "Tie": "purple",
        "Undecided": "grey", # Should not happen for 'Winner_simulated' if logic is correct
        "No Data": "lightgrey"
    }

    fig_map = plot_election_map_plotly(
        st.session_state.us_states_gdf,
        st.session_state.aggregated_results_df,
        column_to_plot='Winner_simulated',
        title="Simulated Election Winner by State",
        color_discrete_map=color_map
    )
    if fig_map:
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.error("Could not generate the election map.")

# --- Display Raw Simulated Voter Data (Optional) ---
st.header("Detailed Simulated Voter Responses (Sample)")
if st.checkbox("Show a sample of individual simulated voter responses"):
    st.dataframe(st.session_state.simulated_profiles_with_votes_df.head(10))

st.markdown("---")
st.markdown("Navigate to the **Data Comparison** page to compare these results with historical data or view adjusted results.")
