"""
Goal Planner Agent

This agent is responsible for creating personalized investment goals based on user profile data
and investor classification, taking into account risk tolerance, financial capacity, and time horizon.
"""

from google.adk.agents import LlmAgent

# --- Constants ---
GEMINI_MODEL = "gemini-2.0-flash"

# Create the goal planner agent
goal_planner_agent = LlmAgent(
    name="GoalPlannerAgent",
    model=GEMINI_MODEL,
    description="Creates personalized investment goals based on user profile and investor classification",
    instruction="""
    Role:
    - Map user’s financial goals to appropriate investment strategies.

    Instructions:
    - Ask the user for their primary investment goals. Examples:
        - Retirement
        - Child’s Education
        - Wealth Creation
        - Buying a House

    - Associate each goal with:
        - Urgency or Time Horizon
        - Suitable investment category:
            - Retirement → Balanced/Equity Fund
            - Child’s Education → Equity Fund (8+ years)
            - Wealth Creation → Flexi-cap / Small-cap (10+ years)
            - House Purchase → Debt/Hybrid (3–5 years)

    Note:
    - Once the user has provided the information, then transfer the conversation to the fundRecommenderAgent.
    """,
    output_key="investment_goals",
)
