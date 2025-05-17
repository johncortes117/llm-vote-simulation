import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px

# --- GeoJSON Loading ---
@st.cache_data # Cache the GeoJSON data for performance
def load_geojson_data():
    """Loads GeoJSON data for U.S. states from a local file or URL."""
    # Prioritize local file if available
    local_geojson_path = "assets/us_states_geo.json"
    try:
        # Attempt to open the local file first
        us_states_gdf = gpd.read_file(local_geojson_path)
        st.info(f"Loaded GeoJSON from local file: {local_geojson_path}")
    except Exception as e_local:
        st.warning(f"Could not load local GeoJSON from '{local_geojson_path}' (Error: {e_local}). Attempting to load from remote URL.")
        # Fallback to remote URL if local file fails or doesn't exist
        remote_geojson_url = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
        try:
            us_states_gdf = gpd.read_file(remote_geojson_url)
            st.info(f"Loaded GeoJSON from remote URL: {remote_geojson_url}")
        except Exception as e_remote:
            st.error(f"Failed to load GeoJSON from both local path and remote URL. Error (remote): {e_remote}")
            return None
    
    # Standardize state name column for merging (e.g., to uppercase)
    if 'name' in us_states_gdf.columns:
        us_states_gdf['STATE_NAME_UPPER'] = us_states_gdf['name'].str.upper()
    elif 'NAME' in us_states_gdf.columns: # Check for other common name variations
        us_states_gdf['STATE_NAME_UPPER'] = us_states_gdf['NAME'].str.upper()
    else:
        st.error("GeoJSON does not have a recognizable state name column (e.g., 'name', 'NAME'). Map plotting will likely fail.")
        # You might return None or the GDF as is, and handle the missing column later
        return us_states_gdf # Or return None
        
    return us_states_gdf

# --- Plotting Functions (using Plotly for interactivity) ---

def plot_election_map_plotly(us_states_gdf, results_df, column_to_plot, title, color_discrete_map=None):
    """
    Generates an interactive U.S. election map using Plotly Express.
    Merges results_df (indexed by uppercase STATE) with us_states_gdf (using 'STATE_NAME_UPPER').
    `column_to_plot` is the column in `results_df` containing the data to visualize (e.g., 'Winner_simulated').
    `color_discrete_map` is a dictionary mapping values in `column_to_plot` to colors.
    """
    if us_states_gdf is None or 'STATE_NAME_UPPER' not in us_states_gdf.columns:
        st.error("GeoJSON data is not loaded correctly or missing standardized state name column. Cannot plot map.")
        return None
    if results_df is None or column_to_plot not in results_df.columns:
        st.error(f"Results data is missing or does not contain the column '{column_to_plot}'. Cannot plot map.")
        return None

    # Ensure results_df index is uppercase for merging
    results_df.index = results_df.index.str.upper()

    # Merge GeoDataFrame with election results
    merged_gdf = us_states_gdf.merge(
        results_df[[column_to_plot]], 
        left_on='STATE_NAME_UPPER', 
        right_index=True, 
        how="left"
    )

    # Fill NaN for states not in results_df (e.g., territories if present in GeoJSON)
    merged_gdf[column_to_plot] = merged_gdf[column_to_plot].fillna("No Data")

    # Define a default color map if none is provided
    if color_discrete_map is None:
        color_discrete_map = {
            "Democrat": "blue",
            "Republican": "red",
            "Tie": "purple",
            "Undecided": "grey",
            "No Data": "lightgrey"
        }
    
    # Ensure all values in the column_to_plot have a color mapping
    # Add any missing values to the color map with a default color
    unique_values_in_plot_col = merged_gdf[column_to_plot].unique()
    for value in unique_values_in_plot_col:
        if value not in color_discrete_map:
            color_discrete_map[value] = "orange" # Default color for unexpected values
            st.warning(f"Value '{value}' in '{column_to_plot}' was not in the provided color map. Assigned default color 'orange'.")

    fig = px.choropleth_mapbox(
        merged_gdf,
        geojson=merged_gdf.geometry,
        locations=merged_gdf.index, # Use the index from the merged GeoDataFrame
        color=column_to_plot,
        mapbox_style="carto-positron", # or "open-street-map"
        zoom=2.5, # Adjusted zoom level for continental U.S.
        center={"lat": 39.8283, "lon": -98.5795}, # Center of U.S.
        opacity=0.7,
        hover_name='STATE_NAME_UPPER', # Show state name on hover
        hover_data={column_to_plot: True}, # Show the winner/data on hover
        color_discrete_map=color_discrete_map,
        title=title
    )
    fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
    return fig


def plot_comparison_bar_chart_plotly(comparison_df, party):
    """
    Generates a grouped bar chart comparing simulated vs. real results for a given party.
    `comparison_df` should have columns like 'Democrat_sim_pct', 'Democrat_real_pct', etc.
    The index of `comparison_df` should be the STATE names.
    """
    sim_col = f'{party}_sim_pct' # Assuming percentage columns are named like this
    real_col = f'{party}_real_pct'
    
    # Check if necessary columns exist, assuming comparison_df might come from different processing steps
    # For this example, we'll assume the notebook's direct vote counts are used for simplicity
    # If using percentages, ensure they are calculated in data_processing.py
    # For now, let's adapt to use direct vote counts if percentage columns aren't there.

    # This part needs to align with how `comparison_df` is structured by `data_processing.py`
    # The notebook example used direct vote counts for comparison bars, not percentages.
    # Let's assume `comparison_df` has 'Democrat_sim', 'Republican_sim', 'Democrat_real', 'Republican_real'
    # (or similar, based on `aggregate_results_by_state` and `compare_simulated_with_real`)

    sim_count_col = f'{party}_sim' # e.g., Democrat_sim (from simulated_results_df part of comparison_df)
    real_count_col = f'{party}_real' # e.g., Democrat_real (from real_results_df part of comparison_df)

    if sim_count_col not in comparison_df.columns or real_count_col not in comparison_df.columns:
        st.warning(f"Columns for {party} comparison ('{sim_count_col}', '{real_count_col}') not found in comparison DataFrame. Bar chart cannot be generated.")
        # Try to find percentage columns if count columns are missing
        # This is just an example; actual column names depend on data_processing.py output
        if f'{party}_simulated' in comparison_df.columns and f'{party}_real_percent' in comparison_df.columns:
            sim_col_to_use = f'{party}_simulated' # This would be raw counts from simulation
            real_col_to_use = f'{party}_real_percent' # This would be percentages from real data
            y_label = "Vote Count (Simulated) vs Vote Percentage (Real)" 
        else:
            return None # Cannot proceed
    else:
        sim_col_to_use = sim_count_col
        real_col_to_use = real_count_col
        y_label = "Number of Votes / Percentage"

    # Prepare data for Plotly (long format)
    plot_data = comparison_df[[sim_col_to_use, real_col_to_use]].copy()
    plot_data.columns = ['Simulated', 'Real'] # Simplify column names for legend
    plot_data['STATE'] = plot_data.index
    plot_data_long = pd.melt(plot_data, id_vars=['STATE'], value_vars=['Simulated', 'Real'],
                             var_name='Data_Type', value_name='Votes_or_Percent')

    fig = px.bar(
        plot_data_long, 
        x='STATE', 
        y='Votes_or_Percent', 
        color='Data_Type', 
        barmode='group',
        title=f"Comparison of Simulated vs. Real Results ({party})",
        labels={'Votes_or_Percent': y_label, 'STATE': 'State'},
        color_discrete_map={"Simulated": "skyblue", "Real": "lightcoral"}
    )
    fig.update_layout(xaxis_tickangle=-45)
    return fig


# --- Matplotlib (Legacy or Specific Use Cases) ---
# The notebook used Matplotlib. Plotly is generally preferred for Streamlit due to interactivity.
# If specific Matplotlib plots are needed, they can be implemented here.
# For example, a direct adaptation of the notebook's Matplotlib map:

def plot_election_map_matplotlib(us_states_gdf, results_df, column_to_plot, title):
    """Generates a U.S. election map using Matplotlib (less interactive)."""
    if us_states_gdf is None or results_df is None:
        st.error("GeoJSON data or results data not loaded. Cannot plot Matplotlib map.")
        return None

    merged_gdf = us_states_gdf.merge(results_df, left_on='STATE_NAME_UPPER', right_index=True, how="left")
    merged_gdf[column_to_plot] = merged_gdf[column_to_plot].fillna("No Data")

    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    merged_gdf.boundary.plot(ax=ax, linewidth=0.8, color="black")
    merged_gdf.plot(column=column_to_plot, ax=ax, legend=True,
                    cmap="coolwarm", 
                    missing_kwds={"color": "lightgrey", "label": "No Data"})
    ax.set_title(title, fontsize=16)
    ax.axis("off")
    return fig # Returns a Matplotlib figure object
