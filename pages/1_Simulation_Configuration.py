import streamlit as st
import pandas as pd
from core.data_processing import load_voter_profiles, load_real_election_data
from core.simulation_logic import get_openai_client, generate_prompt_with_block, run_repeated_simulations

st.set_page_config(page_title="Simulation Configuration", page_icon="⚙️", layout="wide")

st.title("⚙️ Simulation Configuration")

st.markdown("""
This page allows you to configure and run the U.S. Presidential Election simulation.

**Steps:**
1.  **Load Voter Data:** Upload a CSV file with voter profiles or use the default sample data.
2.  **Review Data:** (Optional) Inspect the loaded voter profiles.
3.  **Set Parameters:** Adjust simulation settings, like the number of simulation runs per profile.
4.  **Run Simulation:** Start the simulation process. This may take some time depending on the number of profiles and simulation runs.
""")

# Initialize or load data from session state
if 'voter_profiles_df' not in st.session_state:
    st.session_state.voter_profiles_df = None
if 'simulated_profiles_with_votes_df' not in st.session_state:
    st.session_state.simulated_profiles_with_votes_df = None
if 'real_election_data_df' not in st.session_state:
    st.session_state.real_election_data_df = load_real_election_data()

# --- 1. Load Voter Data ---
st.header("1. Load Voter Data")
uploaded_file = st.file_uploader("Upload Voter Profiles CSV", type=["csv"])

if uploaded_file is not None:
    st.session_state.voter_profiles_df = load_voter_profiles(uploaded_file)
    if st.session_state.voter_profiles_df is not None:
        st.success(f"Successfully loaded {len(st.session_state.voter_profiles_df)} voter profiles from uploaded file.")
elif st.button("Use Default Sample Data") or st.session_state.voter_profiles_df is None:
    st.session_state.voter_profiles_df = load_voter_profiles(None) # Load default
    if st.session_state.voter_profiles_df is not None:
        st.info(f"Using default sample data with {len(st.session_state.voter_profiles_df)} profiles.")

# --- 2. Review Data (Optional) ---
if st.session_state.voter_profiles_df is not None:
    st.header("2. Review Voter Data (Optional)")
    if st.checkbox("Show loaded voter profiles"):
        st.dataframe(st.session_state.voter_profiles_df.head(), height=300)

# --- 3. Set Parameters ---
st.header("3. Set Simulation Parameters")
# Number of simulation runs per profile for ensemble voting
repetitions_per_profile = st.slider(
    "Number of simulation runs per profile (for vote stability):", 
    min_value=1, 
    max_value=10, 
    value=3, 
    help="More repetitions can lead to more stable results but increase simulation time and cost."
)

# --- 4. Run Simulation ---
st.header("4. Run Simulation")
if st.session_state.voter_profiles_df is not None:
    if st.button("Run Election Simulation", type="primary"):
        openai_client = get_openai_client()
        if openai_client:
            with st.spinner(f"Running simulation for {len(st.session_state.voter_profiles_df)} profiles... This may take a while."):
                profiles_to_simulate = st.session_state.voter_profiles_df.copy()
                
                # Ensure real_election_data_df is available for prompt generation
                if st.session_state.real_election_data_df is None:
                    st.error("Real election data not loaded. Cannot generate prompts with political blocks.")
                    st.stop()

                # Generate prompts
                profiles_to_simulate['Prompt'] = profiles_to_simulate.apply(
                    lambda row: generate_prompt_with_block(row, st.session_state.real_election_data_df),
                    axis=1
                )
                
                # Get simulated votes
                votes = []
                progress_bar = st.progress(0)
                total_profiles = len(profiles_to_simulate)
                
                for i, row in profiles_to_simulate.iterrows():
                    vote = run_repeated_simulations(row['Prompt'], openai_client, repetitions=repetitions_per_profile)
                    votes.append(vote)
                    progress_bar.progress((i + 1) / total_profiles)
                
                profiles_to_simulate['Vote'] = votes
                st.session_state.simulated_profiles_with_votes_df = profiles_to_simulate
                progress_bar.empty() # Clear progress bar
            st.success("Simulation completed!")
            st.balloons()
            st.markdown("Navigate to the **Simulated Results** page to view the outcomes.")
        else:
            st.error("OpenAI client could not be initialized. Check API key in secrets.")
    elif st.session_state.simulated_profiles_with_votes_df is not None:
        st.info("Simulation has already been run with the current data. To re-run, click the button above. Results are available on the 'Simulated Results' page.")
else:
    st.warning("Please load voter data before running the simulation.")

st.markdown("---")
st.markdown("Once the simulation is complete, the results will be available on the other pages.")
