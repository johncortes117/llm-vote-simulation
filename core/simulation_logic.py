import openai
import streamlit as st
import numpy as np
from .schemas import NumericVote

def get_openai_client():
    """Initializes and returns the OpenAI client using API key from Streamlit secrets."""
    api_key = st.secrets.get("OPENAI_API_KEY")
    if not api_key:
        st.error("OpenAI API key not found in .streamlit/secrets.toml. Please add it to run the simulation.")
        return None
    return openai.OpenAI(api_key=api_key)

def generate_prompt_with_block(profile_row, real_results_df):
    """
    Generates a personalized prompt for a voter profile, including the political block of their state.
    """
    try:
        # Ensure real_results_df is indexed by STATE (uppercase) for lookup
        state_block = real_results_df.loc[profile_row['STATE'].upper(), 'Block']
    except KeyError:
        state_block = "an unknown political leaning" # Fallback

    prompt = f"""
    You are a {profile_row['AGE']}-year-old {profile_row['GENDER']} voter living in {profile_row['STATE']},
    a state with {state_block}. You have a {profile_row['EDUCATION_LEVEL']} education level.
    You are {profile_row['MARITAL_STATUS']} and work as a {profile_row['OCCUPATION_DESCRIPTION']}.
    Your household income is {profile_row['INCOME_LEVEL']} on a scale of 1 to 10.

    Please cast your vote in the 2024 U.S. presidential election:
    1. KAMALA D. HARRIS / TIM WALZ (Democratic)
    2. DONALD J. TRUMP / J.D. VANCE (Republican)
    Respond with only the number 1 or 2.
    """
    return prompt

def get_voting_response(prompt_content, client):
    """Gets a simulated voting response from the OpenAI API."""
    if not client:
        return "Error_Client_Not_Initialized"
    try:
        response = client.responses.parse(
            model="gpt-4o-mini",
            input=[
                {"role": "system", "content": "Analyze the voter's profile and cast a vote based on the provided schema"},
                {"role": "user", "content": prompt_content},
            ],
            text_format=NumericVote,
        )
        vote = response.output_parsed
        print(f"Vote received: {vote.vote}")
        print(f"Vote type: {type(vote.vote)}")
        return vote.vote
    except Exception as e:
        st.warning(f"API Call Error: {e}")
        return f"Error_API_Call: {str(e)}"

def run_repeated_simulations(prompt_content, client, repetitions=3):
    """
    Runs multiple simulations for a single prompt and returns the most common vote.
    Default repetitions is 3 for cost/time, can be increased.
    """
    if not client:
        return "Error_Client_Not_Initialized"

    raw_votes = []
    for _ in range(repetitions):
        vote = get_voting_response(prompt_content, client)
        raw_votes.append(vote)

    if not raw_votes:
        return "Undecided"

    count_1 = raw_votes.count(1)
    count_2 = raw_votes.count(2)

    if count_1 > count_2:
        return "1"  # Democrat
    elif count_2 > count_1:
        return "2"  # Republican
    elif count_1 == count_2 and count_1 > 0:
        return "1"  # Tie-breaker defaults to 1
    else:
        return "Undecided"
