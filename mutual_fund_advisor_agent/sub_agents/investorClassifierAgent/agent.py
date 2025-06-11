"""
Investor Classifier Agent

This agent is responsible for analyzing user profile data and classifying the investor type
based on various factors including risk tolerance, investment experience, financial situation,
and investment goals.
"""

from google.adk.agents import LlmAgent

# --- Constants ---
GEMINI_MODEL = "gemini-2.0-flash"

# Create the investor classifier agent
investor_classifier_agent = LlmAgent(
    name="InvestorClassifierAgent",
    model=GEMINI_MODEL,
    description = "Evaluates user profile to classify the investor type based on risk appetite and investment horizon.",
    instruction = """
    Role:
    - Analyze the user's risk tolerance and investment horizon to determine their investor type.

    Classification Logic:
    - Low risk + short horizon → Conservative
    - Medium risk + medium horizon → Balanced
    - High risk + long horizon → Aggressive

    Expected Output:
    - One of the following: "Conservative", "Balanced", or "Aggressive"

    Guidelines:
    - Maintain a smooth, natural, and professional tone.
    - Use only validated information already gathered.
    - Do not re-ask questions or repeat answers.
    - Respect user privacy if any data is missing (optional fields).
    - Once classification is done, seamlessly pass the process to the next stage (handled in the background).
    """,
    output_key="investor_type",
)
