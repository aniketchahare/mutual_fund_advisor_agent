from google.adk.agents import LlmAgent
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

GEMINI_MODEL = "gemini-2.0-flash"

# --- Pydantic Output Schema ---

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

class MutualFund(BaseModel):
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

class FundValidationOutput(BaseModel):
    new_funds: Optional[List[MutualFund]] = Field(
        default=None,
        description="List of mutual funds not yet shown to the user"
    )
    message: Optional[str] = Field(
        default=None,
        description="Message when no new funds are available"
    )

# --- Fund Validation Agent Definition ---
fund_validation_agent = LlmAgent(
    name="FundValidationAgent",
    model=GEMINI_MODEL,
    description="Validates if there are new mutual funds to show to the user.",
    instruction="""
    Role:
    - Validate if there are new mutual funds to show to the user.

    Instructions:
    - Accept as input:
        - all_funds: List of all available mutual funds (each with an _id field)
        - shown_fund_ids: List of fund IDs that have already been shown to the user
    - Compare the _id of each fund in all_funds with shown_fund_ids.
    - If all funds in all_funds have their _id in shown_fund_ids, respond with: 'We currently have only these mutual funds available.'
    - If there are funds in all_funds whose _id is not in shown_fund_ids, return only those new funds.
    """,
    output_key="fund_validation_result",
    output_schema=FundValidationOutput
)
