import streamlit as st
import pandas as pd
from core.data_processing import compare_simulated_with_real, adjust_simulated_results
from core.plotting import plot_election_map_plotly, plot_comparison_bar_chart_plotly

st.set_page_config(page_title="Data Comparison", page_icon="📈", layout="wide")

st.title("📈 Data Comparison & Analysis")

# Load data from session state
if 'aggregated_results_df' not in st.session_state or st.session_state.aggregated_results_df is None:
    st.warning("No aggregated simulation results found. Please run a simulation and view results on the '📊 Simulated Results' page first.")
    st.stop()

if 'real_election_data_df' not in st.session_state or st.session_state.real_election_data_df is None:
    st.error("Real election data not loaded. Cannot perform comparison. Check app.py or main page.")
    st.stop()

if 'us_states_gdf' not in st.session_state or st.session_state.us_states_gdf is None:
    st.error("US States GeoJSON data not loaded. Maps cannot be displayed. Check app.py or main page.")
    st.stop()

# --- Perform Comparison ---
if 'comparison_df' not in st.session_state or st.session_state.comparison_df is None:
    st.session_state.comparison_df = compare_simulated_with_real(
        st.session_state.aggregated_results_df.copy(),
        st.session_state.real_election_data_df.copy()
    )

st.header("Comparison: Simulated vs. Real (2020) Election Results")
if st.session_state.comparison_df.empty:
    st.warning("Comparison data is empty. This could be due to issues in merging simulated and real results.")
else:
    st.dataframe(st.session_state.comparison_df)

    # --- Accuracy Metrics (Simple) ---
    if 'Correct_Prediction' in st.session_state.comparison_df.columns:
        correct_predictions = st.session_state.comparison_df['Correct_Prediction'].sum()
        total_comparable_states = st.session_state.comparison_df['Correct_Prediction'].notna().sum()
        if total_comparable_states > 0:
            accuracy = (correct_predictions / total_comparable_states) * 100
            st.metric(label="Prediction Accuracy (vs Real 2020 Winners)", value=f"{accuracy:.2f}%")
        else:
            st.info("No comparable states found to calculate accuracy.")

    # --- Comparative Maps ---
    st.subheader("Comparative Election Maps")
    col1, col2 = st.columns(2)
    
    color_map = {
        "Democrat": "blue",
        "Republican": "red",
        "Tie": "purple",
        "No Data": "lightgrey",
        "No Real Data": "lightgrey" # For the real data map if a state is missing
    }

    with col1:
        st.markdown("**Simulated Results (2024)**")
        fig_sim_map = plot_election_map_plotly(
            st.session_state.us_states_gdf,
            st.session_state.aggregated_results_df, # Use original aggregated for this map
            column_to_plot='Winner_simulated',
            title="Simulated Election Winner",
            color_discrete_map=color_map
        )
        if fig_sim_map:
            st.plotly_chart(fig_sim_map, use_container_width=True)
        else:
            st.error("Could not generate simulated results map.")

    with col2:
        st.markdown("**Real Results (2020)**")
        # Need to pass the correct column from comparison_df or real_election_data_df
        fig_real_map = plot_election_map_plotly(
            st.session_state.us_states_gdf,
            st.session_state.real_election_data_df, # Use the original real data for this map
            column_to_plot='Winner_real',
            title="Real Election Winner (2020)",
            color_discrete_map=color_map
        )
        if fig_real_map:
            st.plotly_chart(fig_real_map, use_container_width=True)
        else:
            st.error("Could not generate real results map.")

    # --- Bar Charts for Vote Comparison (by party) ---
    # This requires comparison_df to have vote counts/percentages like 'Democrat_sim', 'Democrat_real_percent'
    # The plot_comparison_bar_chart_plotly function needs to be adapted or the dataframe columns confirmed.
    # For now, let's assume comparison_df has 'Democrat_sim', 'Republican_sim' (from aggregated) 
    # and 'Democrat_real_percent', 'Republican_real_percent' (from real_election_data)
    
    # To make this work, we need to ensure the comparison_df has the right columns for the bar chart function.
    # Let's prepare a temporary df for this if needed, or adjust the plotting function to be more flexible.
    # The current `plot_comparison_bar_chart_plotly` expects columns like `Party_sim` and `Party_real` (counts or pct)
    # Our `comparison_df` has `Democrat_sim`, `Republican_sim` (counts) and `Democrat_real_percent`, `Republican_real_percent`.
    # We might need to rename or select specific columns for the plotting function.
    
    # For simplicity, let's try to plot if the columns are present. The plotting function has some fallback logic.
    st.subheader("Vote Share Comparison (Simulated Counts vs. Real Percentages)")
    party_to_compare = st.selectbox("Select Party for Detailed Comparison:", ["Democrat", "Republican"])
    
    # Create a temporary DataFrame for plotting, aligning column names if necessary
    # The `plot_comparison_bar_chart_plotly` expects specific column names like `Democrat_simulated` and `Democrat_real`
    # Our `comparison_df` has `Democrat_sim` (counts) and `Democrat_real_percent`.
    # Let's try to make it work by passing a slightly modified df or ensuring the plot function is robust.
    
    # The plotting function was designed for `Party_sim_pct` and `Party_real_pct` or `Party_sim` and `Party_real` (counts)
    # Our comparison_df has `Democrat_sim` (counts) and `Democrat_real_percent`.
    # We need to ensure the plotting function can handle this mix or we provide it what it expects.
    # For now, the plotting function has some logic to try and find relevant columns.
    
    # Let's try to pass the comparison_df directly. The plotting function will try to find appropriate columns.
    # It might be better to prepare specific columns for it.
    # Example: comparison_plot_df = st.session_state.comparison_df[['STATE', f'{party_to_compare}_sim', f'{party_to_compare}_real_percent']].copy()
    # comparison_plot_df.columns = ['STATE', 'Simulated', 'Real']
    # Then pass this to a more generic bar plot function.

    # Given the current `plot_comparison_bar_chart_plotly`, it might struggle with mixed types (counts vs percent)
    # unless explicitly handled. The current version tries to find `_sim` and `_real` suffixes.
    # Let's assume for now the plotting function is robust enough or we adjust it later if issues arise.

    # The `plot_comparison_bar_chart_plotly` was written to expect columns like `Democrat_sim_pct`, `Democrat_real_pct`
    # or `Democrat_sim` (counts), `Democrat_real` (counts). 
    # Our `comparison_df` has `Democrat_sim` (counts from simulation) and `Democrat_real_percent`.
    # This is a mismatch. Let's simplify and plot simulated counts vs real counts if available, or percentages.
    # The `real_election_data_df` has percentages. `aggregated_results_df` has counts.
    # `comparison_df` merges these. So it has `Democrat_sim` (count), `Republican_sim` (count),
    # `Democrat_real_percent`, `Republican_real_percent`.

    # For a fair bar chart comparison, we should compare counts to counts or percentages to percentages.
    # Since we have sim counts and real percentages, a direct bar chart might be misleading without clear labels.
    # The current `plot_comparison_bar_chart_plotly` tries to find `Party_sim` and `Party_real` (expecting same units).

    # Let's focus on comparing WINNERS for now, as the vote share comparison needs careful data alignment for plotting.
    # The bar chart part of the notebook was `ax.bar(x - width/2, comparison["Democrat_simulated"], width, label="Democrat Simulated", color="blue")`
    # `comparison["Democrat_simulated"]` were counts. `comparison["Democrat_real"]` were percentages.
    # This is what the notebook did, so the plotting function should ideally replicate this if that's the goal.
    # The current `plot_comparison_bar_chart_plotly` is more generic.
    # We will skip the bar chart for now as it requires more careful data preparation to match the notebook's mixed-unit plot if desired,
    # or a decision to plot percentages vs percentages (requiring sim percentages to be calculated).
    st.info("Bar chart for detailed vote share comparison (simulated counts vs. real percentages) is pending more specific data alignment for plotting.")


# --- Adjusted Simulation Results (Optional) ---
st.header("Adjusted Simulation Results")
st.markdown("These results are weighted by historical data (2020 election) to potentially provide a more nuanced perspective.")

simulation_weight = st.slider(
    "Weight for Simulated Data (vs. Historical Data for Adjustment):", 
    min_value=0.0, 
    max_value=1.0, 
    value=0.8, 
    step=0.1,
    help="1.0 means 100% simulated data, 0.0 means 100% historical data for the adjusted outcome."
)

if st.button("Calculate Adjusted Results") or (st.session_state.get('adjusted_results_df') is not None and st.session_state.get('last_simulation_weight') != simulation_weight):
    st.session_state.adjusted_results_df = adjust_simulated_results(
        st.session_state.aggregated_results_df.copy(), # Contains Dem/Rep counts
        st.session_state.real_election_data_df.copy(), # Contains Dem/Rep percentages
        simulation_weight=simulation_weight
    )
    st.session_state.last_simulation_weight = simulation_weight # Store last used weight

if st.session_state.get('adjusted_results_df') is not None:
    st.subheader("Adjusted Winner by State")
    st.dataframe(st.session_state.adjusted_results_df)

    fig_adj_map = plot_election_map_plotly(
        st.session_state.us_states_gdf,
        st.session_state.adjusted_results_df,
        column_to_plot='Winner_adjusted',
        title=f"Adjusted Election Winner (Sim Weight: {simulation_weight*100:.0f}%)",
        color_discrete_map=color_map
    )
    if fig_adj_map:
        st.plotly_chart(fig_adj_map, use_container_width=True)
    else:
        st.error("Could not generate the adjusted results map.")
else:
    st.info("Click 'Calculate Adjusted Results' to see the historical data weighted simulation.")
