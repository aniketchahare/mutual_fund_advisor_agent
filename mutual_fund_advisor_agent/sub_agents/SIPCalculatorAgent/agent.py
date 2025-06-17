from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field
from typing import Optional

# --- Constants ---
GEMINI_MODEL = "gemini-2.0-flash"

# Define the output schema using Pydantic
class SIPCalculatorOutput(BaseModel):
    monthly_investment: float = Field(..., description="Monthly SIP amount input by the user (in ₹)")
    investment_duration_years: float = Field(..., description="Duration of SIP investment in years")
    expected_annual_return_rate: float = Field(..., description="Expected annual return rate in percentage (e.g., 12)")
    total_invested: float = Field(..., description="Total amount invested over the period (in ₹)")
    estimated_maturity_value: float = Field(..., description="Estimated future value of the SIP investment (in ₹)")
    estimated_returns: float = Field(..., description="Estimated returns earned over invested amount (in ₹)")
    inflation_adjusted_value: Optional[float] = Field(None, description="Optional: Future value adjusted for user-provided inflation rate")

# Create the SIP Calculator agent
sip_calculator_agent = LlmAgent(
    name="SIPCalculatorAgent",
    model=GEMINI_MODEL,
    description="Estimates future value of investments through SIPs based on user input like monthly investment, duration, and expected return rate. Provides clear, human-readable results.",
    instruction="""
    Role:
    - Help users estimate potential returns from Systematic Investment Plans (SIPs) using user-defined parameters.

    Responsibilities:
    - Ask the user for:
      - Monthly investment amount
      - Investment duration (in years)
      - Expected annual return rate (default: 12%)

    - Calculate:
      - Total invested amount
      - Estimated returns
      - Final future value using the SIP formula:
          FV = P * (((1 + r)^n - 1) / r) * (1 + r)
          Where:
          - P = Monthly investment
          - r = Monthly rate = (annual rate / 12) / 100
          - n = Total months = years × 12

    - Round the final value to the nearest hundred.
    - Present results clearly:
      - Total invested amount
      - Estimated maturity value
      - Estimated returns

    - Optional: Adjust for inflation if user provides a rate

    Tone & Flow:
    - Be conversational and explain calculations in simple terms:
    - E.g., “If you invest ₹10,000 monthly for 10 years at 12%, your investment will grow to approximately ₹23,00,000.”

    Guidelines:
    - Compare variations (amount/duration) if requested.
    - Ask if the user would like to proceed with investing.
    - If yes, return control to the fund recommendation flow where it left off.
    - Remain professional and friendly throughout. Do not address or explain the backend agent handoffs.
    - Do not show any other agent name or tool name to the user.
    - Do not tell user that you are forwarding the interaction to the **MutualFundAdvisorAgent** to handle the next step.
    - Do not show json format to the user.
    - After collecting the necessary information, return the Output in the format of SIPCalculatorOutput.
    - After collecting the necessary information, smoothly forward the interaction to the **MutualFundAdvisorAgent** to handle the next step(this is mandatory to proceed further).
    
    Output Format:
    - Return information in summary format.
        - eg. SIPCalculatorOutput:
            - Monthly investment: 10000
            - Investment duration: 10 years
            - Expected annual return rate: 12%
            - Total invested: 1200000
            - Estimated maturity value: 2300000
            - Estimated returns: 1100000
    """,
    output_key="sip_calculator_output",
)
