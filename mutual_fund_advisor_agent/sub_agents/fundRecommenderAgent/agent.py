import os

from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field
from typing import List, Literal, Dict, Any
from datetime import datetime
import requests
from google.adk.tools.agent_tool import AgentTool
from .validation_agent import fund_validation_agent

# --- Constants ---
GEMINI_MODEL = "gemini-2.0-flash"
BASE_URL = os.getenv("MUTUAL_FUND_SERVER_BASE_URL")

# --- Output Schema using Pydantic ---
class FundReturn(BaseModel):
    _1W: float
    _1M: float
    _3M: float
    _6M: float
    YTD: float
    _1Y: float
    _2Y: float
    _3Y: float
    _5Y: float
    _10Y: float

class RecommendedFund(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    risk_level: str
    fund_type: str
    category: str
    min_sip_amount: float
    nav: float
    fund_size: float
    is_active: bool
    returns: FundReturn
    createdAt: datetime
    updatedAt: datetime
    recommendation_reason: str = Field(..., description="Why this fund was recommended")

class FundRecommendationOutput(BaseModel):
    recommended_funds: List[RecommendedFund] = Field(..., description="Top 2–3 funds recommended to the user")

# --- Fund Fetcher ---
def fetch_funds_api() -> List[Dict[str, Any]]:
    """Fetch mutual funds from the local API and return the data as a list of dicts following the schema."""
    response = requests.get(f"{BASE_URL}/funds")
    response.raise_for_status()
    return response.json()

# --- LLM Agent Definition ---
fund_recommender_agent = LlmAgent(
    name="FundRecommenderAgent",
    model=GEMINI_MODEL,
    description="Suggests mutual funds tailored to the user's profile, investor type, and financial goals.",
    instruction="""
    Role:
    - Recommend mutual funds based on the user's risk profile, goals, and investment preferences.

    Responsibilities:
    - Fetch funds using fetch_funds_api(this is a tool call, make sure to use this tool call to fetch the funds no other way) and recommend 2–3 options based on investor type:
      - Conservative → Debt or Liquid Funds
      - Balanced → Hybrid or Large-cap Funds
      - Aggressive → Small-cap, Flexi-cap, or Thematic Funds
    - Provide a reason for each recommended fund (e.g., strong returns, suitability for goal).
    - Track shown_fund_ids to avoid duplicates and use fund_validation_agent if needed.

    Return Calculation:
    - For SIP return estimation, ask for monthly amount, duration, and expected return rate (default 12%)
    - Consider the fund_id of the fund selected by the user to calculate the return.
    - Use default rate of return as (12%) for the fund selected by the user if not provided by the user.
    - Delegate SIP calculation to SIPCalculatorAgent and resume recommendation.

    💰 Investment Flow:
    - After recommendations, ask:
      "Would you like to invest in any of these using SIP or lumpsum?"
    - If YES, delegate to InvestmentAgent.

    Guidelines:
    - Always fetch the funds using fetch_funds_api(this is a tool call, make sure to use this tool call to fetch the funds no other way) before recommending the funds.
    - Be friendly, clear, and professional
    - Collect the data by asking one question at a time and give options to choose from.
    - Ask each question with ShowOption enabled
        - in a new line & give a options to choose from in new line.
        - eg. Recommended funds:
            - 1. Axis Small Cap Fund
            - 2. ICICI Prudential Small Cap Fund
            - 3. HDFC Small Cap Fund
    - Set/update the user input or answer in the format of FundRecommendationOutput one by one.
    - Do not expose backend function names or logic
    - Validate user inputs when applicable
    - Use defaults smartly (e.g., current date for SIP start)
    - End with:
      "Thanks again! We're here whenever you need personalized investment advice."
    - Do not show any other agent name or tool name to the user.
    - Do not tell user that you are forwarding the interaction to the **MutualFundAdvisorAgent** to handle the next step.
    - Do not show json format to the user.
    - After collecting the necessary information, return the Output in the format of FundRecommendationOutput.
    - After collecting the necessary information, smoothly forward the interaction to the **MutualFundAdvisorAgent** to handle the next step(this is mandatory to proceed further).
    
    Output Format:
    - Return information in summary format.
        - eg. FundRecommendationOutput:
            - Recommended funds:
                - Axis Small Cap Fund
                - ICICI Prudential Small Cap Fund
                - HDFC Small Cap Fund
    """,
    output_key="fund_recommendation",
    tools=[fetch_funds_api, AgentTool(fund_validation_agent)],
)
