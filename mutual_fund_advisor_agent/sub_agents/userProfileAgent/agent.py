"""
User Profile Agent

This agent is responsible for collecting and validating all necessary user information
required for investment planning and mutual fund recommendations.
"""

from google.adk.agents import LlmAgent

# --- Constants ---
GEMINI_MODEL = "gemini-2.0-flash"

# Create the user profile agent
user_profile_agent = LlmAgent(
   name="UserProfileAgent",
   model=GEMINI_MODEL,
   description="Collects and validates comprehensive user information for investment planning",
   instruction="""
   Role:
   - Collect structured user information required for investment planning.

   Instructions:
   Ask the user the following:

   - Age
   - Monthly Income
   - Assets (optional, like FDs, gold, real estate)
   - Existing Investments (PPF, MF, stocks, etc.)
   - Risk Tolerance: (Low / Medium / High)
   - Investment Horizon: (in years)
   - Investment Mode Preference: (SIP / Lumpsum / Hybrid)
   - Experience Level: (Beginner / Intermediate / Advanced)

   Note:
   - All information is required.
   - Do not respond same questions and answers multiple times once you have the information.
   - Ensure all questions are answered in a conversational manner.
   - If the user doesn't want to share certain information, respect their privacy.
   - Validate the user's responses to ensure they are valid.
   - If the user's response is not valid, ask them to clarify or provide a different answer.
    """,
    output_key="user_profile",
)
