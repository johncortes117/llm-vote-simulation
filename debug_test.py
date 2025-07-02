
import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.simulation_logic import get_openai_client, generate_prompt_with_block, get_voting_response
from core.data_processing import load_real_election_data
import pandas as pd

def run_debug_test():
    """
    Runs a single simulation for a specific voter profile to debug the model's response.
    """
    # 1. Initialize OpenAI Client
    client = get_openai_client()
    if not client:
        print("Error: OpenAI client could not be initialized. Check your API key.")
        return

    # 2. Load real election data to get the 'Block' for the state
    real_results_df = load_real_election_data()

    # 3. Define a single voter profile for the test
    profile_data = {
        "AGE": [35],
        "GENDER": ["female"],
        "STATE": ["Florida"],
        "EDUCATION_LEVEL": ["bachelor"],
        "MARITAL_STATUS": ["married"],
        "OCCUPATION_DESCRIPTION": ["teacher"],
        "INCOME_LEVEL": [5]
    }
    profile_df = pd.DataFrame(profile_data)
    test_profile = profile_df.iloc[0]

    # 4. Generate the prompt
    prompt = generate_prompt_with_block(test_profile, real_results_df)
    print("--- Generated Prompt ---")
    print(prompt)
    print("------------------------")

    # 5. Get the voting response from the model
    print("Requesting vote from the model...")
    vote_response = get_voting_response(prompt, client)

    # 6. Print the raw response
    print("--- Model's Raw Response ---")
    if hasattr(vote_response, 'vote'):
        print(f"Vote: {vote_response.vote}")
    else:
        print(f"Response: {vote_response}")
    print("----------------------------")

if __name__ == "__main__":
    run_debug_test()
