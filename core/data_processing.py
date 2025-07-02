import pandas as pd
import streamlit as st

# --- Data Loading and Preprocessing ---

def load_voter_profiles(uploaded_file):
    
    """Loads voter profiles from a CSV file or uses a default."""
    
    if uploaded_file is not None:
        try:
            profiles_df = pd.read_csv(uploaded_file)
            
            # Basic validation: Check for essential columns (adjust as needed)
            essential_cols = ['AGE', 'GENDER', 'STATE', 'EDUCATION_LEVEL', 'MARITAL_STATUS', 'OCCUPATION_DESCRIPTION', 'INCOME_LEVEL']
            
            if not all(col in profiles_df.columns for col in essential_cols):
                st.error(f"Uploaded CSV is missing one or more essential columns: {essential_cols}")
                return None
            
            return profiles_df
        
        except Exception as e:
            st.error(f"Error reading or parsing the uploaded CSV: {e}")
            return None
    else:
        # Use a small default dataset if no file is uploaded
        st.info("No CSV uploaded. Using a default sample of voter profiles.")
        
        data = {
            "AGE": [25, 40, 60, 35, 50, 45, 29, 38, 67, 53],
            "GENDER": ["male", "female", "female", "male", "male", "female", "male", "female", "male", "female"],
            "STATE": ["California", "Texas", "New York", "Florida", "Ohio", "Pennsylvania", "Illinois", "Michigan", "Georgia", "Arizona"],
            "EDUCATION_LEVEL": ["bachelor", "master", "high_school", "bachelor", "phd", "high_school", "master", "bachelor", "high_school", "master"],
            "MARITAL_STATUS": ["single", "married", "widowed", "single", "married", "single", "married", "single", "widowed", "divorced"],
            "OCCUPATION_DESCRIPTION": ["engineer", "teacher", "retired", "manager", "scientist", "nurse", "lawyer", "technician", "consultant", "artist"],
            "INCOME_LEVEL": [6, 4, 3, 7, 9, 5, 4, 6, 3, 7]
        }
        return pd.DataFrame(data)

def load_real_election_data():
    
    """Loads a predefined DataFrame of real election results (e.g., 2020)."""
    
    real_results = {
        "STATE": ["CALIFORNIA", "TEXAS", "NEW YORK", "FLORIDA", "OHIO", "PENNSYLVANIA", "ILLINOIS", "MICHIGAN", "GEORGIA", "ARIZONA"],
        "Democrat_real_percent": [63.5, 46.5, 60.9, 47.9, 45.2, 50.0, 57.9, 50.6, 49.5, 49.4],
        "Republican_real_percent": [34.3, 52.1, 37.7, 51.2, 53.3, 48.8, 40.6, 47.8, 49.3, 49.1],
        "Winner_real": ["Democrat", "Republican", "Democrat", "Republican", "Republican", "Democrat", "Democrat", "Democrat", "Democrat", "Democrat"],
        "Block": ["solidly Democratic", "solidly Republican", "solidly Democratic", "swing state", "swing state", "swing state", "solidly Democratic", "swing state", "swing state", "swing state"]
    }
    
    real_results_df = pd.DataFrame(real_results)
    real_results_df.set_index("STATE", inplace=True)
    return real_results_df

# --- Simulation Results Processing ---

def process_simulated_votes(profiles_df):
    
    """Processes simulated votes, cleans them, and maps to party names."""
    
    if 'Vote' not in profiles_df.columns:
        st.error("'Vote' column not found in profiles. Simulation might have failed or not run.")
        return profiles_df # Return original if 'Vote' is missing

    # Define a mapping for votes
    vote_map = {"1": "Democrat", "2": "Republican"}

    # Apply the mapping. Use .get to provide a default value ('Undecided') for any vote not in the map.
    profiles_df['Vote_Party'] = profiles_df['Vote'].astype(str).apply(lambda x: vote_map.get(x.strip(), "Undecided"))

    return profiles_df

def aggregate_results_by_state(profiles_with_party_votes_df):
    """Aggregates simulated votes by state to determine a winner."""
    if 'Vote_Party' not in profiles_with_party_votes_df.columns or 'STATE' not in profiles_with_party_votes_df.columns:
        st.error("Required columns for aggregation (STATE, Vote_Party) are missing.")
        # Return an empty DataFrame or a specific structure indicating failure
        return pd.DataFrame(columns=['Democrat', 'Republican', 'Undecided', 'Winner_simulated'])

    # Ensure STATE is uppercase for consistent grouping
    profiles_with_party_votes_df['STATE'] = profiles_with_party_votes_df['STATE'].str.upper()

    # Count votes per party per state
    results_by_state = profiles_with_party_votes_df.groupby('STATE')['Vote_Party'].value_counts().unstack().fillna(0)

    # Ensure Democrat, Republican, and Undecided columns exist
    for party_col in ['Democrat', 'Republican', 'Undecided']:
        if party_col not in results_by_state.columns:
            results_by_state[party_col] = 0

    # Determine the winner, excluding "Undecided" from winning
    # Create a temporary DataFrame for winner calculation without 'Undecided' influencing the max
    winner_calc_df = results_by_state[['Democrat', 'Republican']].copy()
    results_by_state['Winner_simulated'] = winner_calc_df.idxmax(axis=1)

    # Handle ties: if Democrat and Republican counts are equal, mark as Tie or Undecided
    # This condition needs to be carefully checked after idxmax
    tie_condition = results_by_state['Democrat'] == results_by_state['Republican']
    results_by_state.loc[tie_condition, 'Winner_simulated'] = "Tie"

    return results_by_state[['Democrat', 'Republican', 'Undecided', 'Winner_simulated']]


# --- Comparison Logic (from notebook) ---

def compare_simulated_with_real(simulated_results_df, real_results_df):
    """Merges simulated results with real results for comparison."""
    # Ensure STATE index is uppercase for both DataFrames before merging
    simulated_results_df.index = simulated_results_df.index.str.upper()
    real_results_df.index = real_results_df.index.str.upper()

    comparison_df = simulated_results_df.merge(
        real_results_df, 
        left_index=True, 
        right_index=True, 
        how="left", # Use left merge to keep all simulated states
        suffixes=["_sim", "_real"] # _sim from simulated_results_df, _real from real_results_df
    )
    
    # Fill NaN for states present in simulation but not in real_results_df (if any)
    # For winner columns, fill with a placeholder like "No Real Data"
    if 'Winner_real' in comparison_df.columns:
        comparison_df['Winner_real'].fillna("No Real Data", inplace=True)
    if 'Block' in comparison_df.columns: # Block comes from real_results_df
        comparison_df['Block'].fillna("Unknown Block", inplace=True)

    # Calculate if prediction was correct (only for states with real data)
    if 'Winner_simulated' in comparison_df.columns and 'Winner_real' in comparison_df.columns:
        comparison_df['Correct_Prediction'] = (comparison_df['Winner_simulated'] == comparison_df['Winner_real']) & (comparison_df['Winner_real'] != "No Real Data")
    else:
        comparison_df['Correct_Prediction'] = False # Or pd.NA

    return comparison_df


def adjust_simulated_results(simulated_df, real_df, simulation_weight=0.8):
    """Adjusts simulated results by weighting them with real historical data."""
    adjusted_dict = {}
    
    # Ensure indices are uppercase for consistent lookup
    simulated_df.index = simulated_df.index.str.upper()
    real_df.index = real_df.index.str.upper()

    for state_name in simulated_df.index:
        sim_dem_votes = simulated_df.loc[state_name, 'Democrat']
        sim_rep_votes = simulated_df.loc[state_name, 'Republican']
        
        # Calculate total simulated votes for percentage calculation
        total_sim_votes = sim_dem_votes + sim_rep_votes
        # Avoid division by zero if a state had 0 Dem and 0 Rep votes (e.g. only Undecided)
        sim_dem_pct = (sim_dem_votes / total_sim_votes) * 100 if total_sim_votes > 0 else 0
        sim_rep_pct = (sim_rep_votes / total_sim_votes) * 100 if total_sim_votes > 0 else 0

        if state_name in real_df.index:
            real_dem_pct = real_df.loc[state_name, 'Democrat_real_percent']
            real_rep_pct = real_df.loc[state_name, 'Republican_real_percent']
            
            adj_dem_pct = (simulation_weight * sim_dem_pct) + ((1 - simulation_weight) * real_dem_pct)
            adj_rep_pct = (simulation_weight * sim_rep_pct) + ((1 - simulation_weight) * real_rep_pct)
        else:
            # If no real data for the state, use simulated percentages directly
            adj_dem_pct = sim_dem_pct
            adj_rep_pct = sim_rep_pct
            
        winner = "Democrat" if adj_dem_pct > adj_rep_pct else "Republican"
        if adj_dem_pct == adj_rep_pct: # Handle ties in adjusted percentages
            winner = "Tie"
            
        adjusted_dict[state_name] = {
            "Democrat_adj_pct": adj_dem_pct,
            "Republican_adj_pct": adj_rep_pct,
            "Winner_adjusted": winner
        }
    
    adjusted_final_df = pd.DataFrame.from_dict(adjusted_dict, orient='index')
    return adjusted_final_df
