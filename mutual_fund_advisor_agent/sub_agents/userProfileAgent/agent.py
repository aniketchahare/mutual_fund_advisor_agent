"""
User Profile Agent

This agent is responsible for collecting and validating all necessary user information
required for investment planning and mutual fund recommendations.
"""

from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field
from typing import List, Optional

# --- Constants ---
GEMINI_MODEL = "gemini-2.0-flash"

# --- Output Schema using Pydantic ---
class UserProfileOutput(BaseModel):
    name: str = Field(..., description="Name of the user")
    age: int = Field(..., description="Age of the user")
    monthly_income: float = Field(..., description="User's monthly income in INR")
    assets: Optional[List[str]] = Field(None, description="Optional list of assets like FDs, gold, property")
    existing_investments: List[str] = Field(..., description="Existing investments like PPF, MF, stocks")
    risk_tolerance: str = Field(..., description="Risk appetite: Low, Medium, or High")
    investment_horizon_years: int = Field(..., description="Number of years user wants to stay invested")
    preferred_investment_mode: str = Field(..., description="SIP, Lumpsum, or Hybrid")
    investment_experience: str = Field(..., description="Beginner, Intermediate, or Advanced")


# Create the user profile agent
user_profile_agent = LlmAgent(
   name="UserProfileAgent",
   model=GEMINI_MODEL,
    description = "Gathers and validates essential user details to enable personalized investment planning.",
    instruction = """
    Role:
    - Collect structured user information required to begin mutual fund planning.

    Responsibilities:
    - Engage the user naturally and professionally to gather the following:
    - Name
    - Age
    - Monthly income
    - Assets (e.g., FDs, gold, property) – optional
    - Existing investments (e.g., PPF, MF, stocks)
    - Risk tolerance (Low / Medium / High) - ShowOption enabled
    - Investment horizon (in years) - ShowOption enabled
    - Preferred investment mode (SIP / Lumpsum / Hybrid) - ShowOption enabled
    - Investment experience (Beginner / Intermediate / Advanced) - ShowOption enabled

    Guidelines:
    - Ensure a smooth, conversational tone — like a friendly, professional discussion.
    - Confirm responses are valid and complete.
    - Collect the data by asking one question at a time and give options to choose from.
    - Ask each question with ShowOption enabled
        - in a new line & give a options to choose from in new line.
        - eg. Risk tolerance:
            - 1. Low
            - 2. Medium
            - 3. High
    - Set/update the user input or answer in the format of UserProfileOutput one by one.
    - If unclear or invalid, politely ask for clarification.
    - Respect privacy if the user skips any optional details.
    - Avoid repeating questions once answers are received.
    - Do not show any other agent name or tool name to the user.
    - Do not tell user that you are forwarding the interaction to the **InvestorClassifierAgent** to handle the next step.
    - Do not tell user that you are transfering the calls to agents.
    - Keep the conversation focused and professional.
    - Do not show json format to the user.
    - After collecting the necessary information, smoothly forward the interaction to the **InvestorClassifierAgent** to handle the next step(this is mandatory to proceed further).
    - Once all key details are collected, return the Output in the format of UserProfileOutput.
    
    Output Format:
    - Return information in summary format.
        - eg. UserProfileOutput:
            - Name: John Doe
            - Age: 30
            - Monthly income: 50000
            - Assets: FDs, gold, property
            - Existing investments: PPF, MF, stocks
    """,
    output_key="user_profile",
)
