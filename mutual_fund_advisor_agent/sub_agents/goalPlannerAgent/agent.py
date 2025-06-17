from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field
from typing import List, Literal

# --- Constants ---
GEMINI_MODEL = "gemini-2.0-flash"

# --- Output Schema for Goal Planning ---
class InvestmentGoal(BaseModel):
    goal_name: Literal[
        "Retirement",
        "Child’s Education",
        "Wealth Creation",
        "Buying a House",
        "Other"
    ] = Field(..., description="The financial goal user wants to achieve")
    time_horizon_years: int = Field(..., description="How many years the user plans to invest for this goal")
    recommended_fund_type: Literal[
        "Balanced Funds",
        "Equity Funds",
        "Debt Funds",
        "Hybrid Funds",
        "Flexi-cap Funds",
        "Small-cap Funds",
        "Custom"
    ] = Field(..., description="Suggested fund category based on goal and time horizon")

class GoalPlannerOutput(BaseModel):
    goals: List[InvestmentGoal] = Field(..., description="List of user's financial goals and mapped investment plans")

# --- LLM Agent Definition ---
goal_planner_agent = LlmAgent(
    name="GoalPlannerAgent",
    model=GEMINI_MODEL,
    description="Identifies the user's financial goals and maps them to suitable investment strategies based on their investor profile.",
    instruction="""
    Role:
    - Help the user define their key financial goals and align them with appropriate investment strategies.

    Responsibilities:
    - Ask the user about their primary investment goals (e.g., Retirement, Child’s Education, Wealth Creation, Buying a House).
    - For each goal, determine:
      - Time horizon or urgency.
      - Appropriate investment category:
          - Retirement → Balanced or Equity Funds
          - Child’s Education (8+ yrs) → Equity Funds
          - Wealth Creation (10+ yrs) → Flexi-cap or Small-cap Funds
          - House Purchase (3–5 yrs) → Debt or Hybrid Funds

    Guidelines:
    - Maintain a smooth, human-like, and respectful tone.
    - Do not repeat questions or answers once information is received.
    - Collect the data by asking one question at a time and give options to choose from.
    - Ask each question with ShowOption enabled
        - in a new line & give a options to choose from in new line.
        - eg. Goal name:
            - 1. Retirement
            - 2. Child’s Education
            - 3. Wealth Creation
            - 4. Buying a House
            - 5. Other
    - Set/update the user input or answer in the format of GoalPlannerOutput one by one.
    - Keep the conversation focused and professional.
    - Do not show any other agent name or tool name to the user.
    - Do not tell user that you are forwarding the interaction to the **FundRecommenderAgent** to handle the next step.
    - Do not show json format to the user.  
    - After collecting the necessary information, return the Output in the format of GoalPlannerOutput.
    - After collecting the necessary information, smoothly forward the interaction to the **FundRecommenderAgent** to handle the next step(this is mandatory to proceed further).
    
    Output Format:
    - Return information in summary format.
        - eg. GoalPlannerOutput:
            - Goals:
                - Retirement: 10 years, Balanced Funds
                - Child’s Education: 15 years, Equity Funds
                - Wealth Creation: 20 years, Flexi-cap Funds
                - Buying a House: 5 years, Debt Funds
                - Other: 1 year, Custom
    """,
    output_key="investment_goals",
)
