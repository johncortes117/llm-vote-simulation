# U.S. Presidential Election Simulator

## Overview
The U.S. Presidential Election Simulator is a Python-based web application designed to simulate U.S. presidential election outcomes. It utilizes demographic voter profiles and leverages OpenAI's GPT-3.5-turbo model to predict voting intentions. This project, originally conceived as a Jupyter Notebook, is being developed as an interactive web application using Streamlit to provide a user-friendly interface for exploring potential election scenarios.

The core idea is to model individual voter behavior based on a set of demographic attributes and then aggregate these simulated intentions to predict state-level and national election results.

## Key Features
*   **Voter Profile Input:** Allows users to input or upload CSV files containing demographic profiles for simulated voters. Attributes include Age, Gender, State, Education Level, Marital Status, Occupation, and Income Level.
*   **Dynamic Prompt Generation:** Generates personalized prompts for each voter profile to query their voting intention in a hypothetical 2024 U.S. presidential election (candidates: Kamala D. Harris/Tim Walz vs. Donald J. Trump/J.D. Vance).
*   **LLM-Powered Prediction:** Uses the OpenAI API (GPT-3.5-turbo) to obtain simulated voting responses (Democrat or Republican) based on the generated prompts.
*   **Results Aggregation:** Processes and aggregates the simulated votes to determine a winning party for each state.
*   **Interactive Visualization:** Visualizes the simulated election results on a U.S. map, clearly showing the winning party per state.
*   **Comparative Analysis:** Optionally, allows users to compare simulated results with historical election data (e.g., 2020 election results).
*   **(Planned) Advanced Simulation:** Potential for features like adjusting simulated results based on real-time data or running multiple simulation iterations per profile for robustness.

## Technology Stack
*   **Python:** Core programming language.
*   **Streamlit:** For building the interactive web application interface.
*   **Pandas:** For data manipulation, analysis, and handling voter profile data.
*   **OpenAI Python library:** To interact with the GPT models for simulating voter responses.
*   **GeoPandas & Matplotlib/Plotly:** For creating U.S. state map visualizations of election results. (Note: Plotly might be preferred for interactive Streamlit charts).

## Project Structure
The project is organized into the following main directories:

*   `election_simulator_streamlit/`
    *   `app.py`: The main script for the Streamlit application (serves as the home page or entry point).
    *   `pages/`: Contains individual Streamlit pages for multi-page applications (e.g., simulation setup, results display).
        *   `1_Simulation_Configuration.py`: Page for configuring simulation parameters.
        *   `2_Simulated_Results.py`: Page for displaying simulated results.
        *   `3_Data_Comparison.py`: Page for comparing with historical data.
    *   `core/`: Contains the core logic of the simulation.
        *   `simulation_logic.py`: Functions for generating prompts, interacting with the OpenAI API, etc.
        *   `data_processing.py`: Functions for loading, cleaning, transforming, and aggregating data.
        *   `plotting.py`: Functions for generating maps and other visualizations.
    *   `utils/`: Contains general utility functions.
        *   `helpers.py`: Helper functions for tasks like file loading, generic validations, etc.
    *   `assets/`: Stores static files.
        *   `logo.png`: Application logo.
        *   `plantilla_perfiles.csv`: Template CSV for voter profiles.
        *   `us_states_geo.json`: GeoJSON file for U.S. states map (if bundled locally).
    *   `.streamlit/`: Directory for Streamlit-specific configuration.
        *   `config.toml`: Application configuration (e.g., theme, layout).
        *   `secrets.toml`: **Crucial for storing API keys and other sensitive information.**
    *   `requirements.txt`: Lists all Python dependencies for the project.
    *   `README.md`: This file - provides an overview and instructions for the project.

## Prerequisites
Before you begin, ensure you have the following installed:
*   Python (version 3.8 or higher recommended)
*   pip (Python package installer)

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/johncortes117/llm-vote-simulation.git
    cd llm-vote-simulation
    ```

2.  **Create and activate a virtual environment (recommended):**
    *   On Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Install dependencies:**
    Install all required packages from `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

**OpenAI API Key Setup (VERY IMPORTANT):**

To use the simulation features that rely on OpenAI's models, you need to configure your OpenAI API key.

1.  Create a file named `secrets.toml` inside the `.streamlit` directory (i.e., `llm-vote-simulation/.streamlit/secrets.toml`).
2.  Add your OpenAI API key to this file in the following format:

    ```toml
    # .streamlit/secrets.toml

    OPENAI_API_KEY = "sk-YourActualOpenAIapiKeyGoesHere"
    ```

    **Replace `"sk-YourActualOpenAIapiKeyGoesHere"` with your actual OpenAI API key.**

    *Note: Ensure that `.streamlit/secrets.toml` is listed in your `.gitignore` file to prevent accidentally committing your API key to version control.* The provided `.gitignore` should already include `.streamlit/`.

## How to Run the Application

Once the setup and configuration are complete, you can run the Streamlit application using the following command in your terminal (from the `election_simulator_streamlit` directory):

```bash
streamlit run app.py
```

This will typically open the application in your default web browser.

## Usage
(This section can be expanded as the application develops)

1.  **Navigate to the Application:** Open the URL provided by Streamlit when you run the app (usually `http://localhost:8501`).
2.  **Configure Simulation:** Go to the "Simulation Configuration" page. Here you can:
    *   Upload a CSV file with voter profiles (use the `assets/plantilla_perfiles.csv` as a template).
    *   Or manually input voter data (if this feature is implemented).
    *   Set any other simulation parameters.
3.  **Run Simulation:** Initiate the simulation process. The app will generate prompts, query the OpenAI API, and process the responses.
4.  **View Results:** Navigate to the "Simulated Results" page to see the aggregated results, including the U.S. map visualization showing the winning party per state.
5.  **Compare Data:** (If implemented) Use the "Data Comparison" page to compare your simulation against historical data.

## To-Do / Future Enhancements
*   Implement more sophisticated demographic weighting.
*   Allow users to select different LLM models or adjust model parameters.
*   Integrate more detailed historical election datasets for comparison.
*   Add functionality to save and load simulation configurations and results.
*   Improve error handling and user feedback.
*   Expand the range of demographic attributes.
*   Conduct sensitivity analysis on different demographic factors.
*   Develop more advanced visualizations and analytical tools.