"""
User Profile Agent

This agent is responsible for collecting and validating all necessary user information
required for investment planning and mutual fund recommendations.
"""

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import ToolContext
from typing import Dict, Any

# --- Constants ---
GEMINI_MODEL = "gemini-2.0-flash"

# --- Tool to update specific user_profile fields ---
def set_user_profile_field(tool_context: ToolContext, field: str, value: str) -> Dict:
    # Get user_profile, ensure it's a dict
    profile = tool_context.state.get("user_profile")

    # If it's None or a Pydantic model, convert it to a dict
    if profile is None:
        profile = {}
    elif hasattr(profile, "dict"):
        profile = profile.dict()

    # Update field
    profile[field] = value

    # Assign back to tool_context
    tool_context.state["user_profile"] = profile

    return {
        "action": "set_user_profile_field",
        "data": profile,
        "message": f"Set user_profile.{field} to {value}",
    }

# Create the user profile agent
user_profile_agent = LlmAgent(
   name="UserProfileAgent",
   model=GEMINI_MODEL,
    description = "Gathers and validates essential user details to enable personalized investment planning.",
    instruction = """
    Role:
    - Collect structured user information required to begin mutual fund planning.

    Responsibilities:
    - Collect the data by asking one question at a time and give options to choose from.
    - set_user_profile_field tool is used to set the user_profile field in the session state.
        - eg. set_user_profile_field(tool_context, "name", "John Doe")
        - eg. set_user_profile_field(tool_context, "age", 30)
        - eg. set_user_profile_field(tool_context, "monthly_income", 50000)
        - eg. set_user_profile_field(tool_context, "assets", "FDs, gold, property")
        - eg. set_user_profile_field(tool_context, "existing_investments", "PPF, MF, stocks")
        - eg. set_user_profile_field(tool_context, "risk_tolerance", "Low")
        - eg. set_user_profile_field(tool_context, "investment_horizon", 10)
        - eg. set_user_profile_field(tool_context, "preferred_investment_mode", "SIP")
        - eg. set_user_profile_field(tool_context, "investment_experience", "Beginner")
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
    """,
    # output_key="user_profile",
    tools=[set_user_profile_field],
)
