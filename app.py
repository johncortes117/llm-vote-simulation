import streamlit as st

st.set_page_config(
    page_title="U.S. Election Simulator",
    page_icon="🗳️",
    layout="wide"
)

st.title("🗳️ U.S. Presidential Election Simulator")

st.markdown("""
Welcome to the U.S. Presidential Election Simulator!

This application uses demographic voter profiles and OpenAI's GPT models to predict voting intentions
and simulate potential election outcomes.

**Navigate through the pages using the sidebar to:**
- **Configure Simulation:** Set up voter profiles and run the simulation.
- **View Simulated Results:** See the predicted outcomes on a U.S. map and in tables.
- **Compare Data:** Analyze simulated results against historical data.

**Project Overview:**
The core idea is to model individual voter behavior based on a set of demographic attributes
and then aggregate these simulated intentions to predict state-level and national election results.
""")

st.sidebar.success("Select a page above to begin.")

st.markdown("---")
st.markdown("### Technology Stack")
st.markdown("""
- **Python:** Core programming language.
- **Streamlit:** For the interactive web application interface.
- **Pandas:** For data manipulation and analysis.
- **OpenAI API:** For simulating voter responses.
- **Plotly & GeoPandas:** For map visualizations.
""")

st.markdown("---")
st.info("This is a simulation tool and results are illustrative. Real-world elections are influenced by a multitude of complex factors.")

# Initialize session state variables if they don't exist
if 'voter_profiles_df' not in st.session_state:
    st.session_state.voter_profiles_df = None
if 'simulated_profiles_with_votes_df' not in st.session_state:
    st.session_state.simulated_profiles_with_votes_df = None
if 'aggregated_results_df' not in st.session_state:
    st.session_state.aggregated_results_df = None
if 'comparison_df' not in st.session_state:
    st.session_state.comparison_df = None
if 'adjusted_results_df' not in st.session_state:
    st.session_state.adjusted_results_df = None
if 'real_election_data_df' not in st.session_state:
    # Load it once and store in session state if needed globally or for quick access
    from core.data_processing import load_real_election_data
    st.session_state.real_election_data_df = load_real_election_data()
if 'us_states_gdf' not in st.session_state:
    from core.plotting import load_geojson_data
    st.session_state.us_states_gdf = load_geojson_data()

