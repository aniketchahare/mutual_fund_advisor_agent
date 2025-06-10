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
   description="Analyzes user profile data to classify investor type and risk profile",
   instruction="""
   Role:
   - Classify the investor type based on risk tolerance and investment horizon.

   Instructions:
   Use this logic:
   - Low Risk + Short Horizon → Conservative
   - Medium Risk + Medium Horizon → Balanced
   - High Risk + Long Horizon → Aggressive

   Return one of:
   - "Conservative"
   - "Balanced"
   - "Aggressive"

   Note:
   - Do not respond same questions and answers multiple times once you have the information.
   - If the user doesn't want to share certain information, respect their privacy.
   - Validate the user's responses to ensure they are valid.
   - If the user's response is not valid, ask them to clarify or provide a different answer.
   - Once the investor type is classified, then transfer the conversation to the goal_planner_agent.
    """,
    output_key="investor_type",
)
