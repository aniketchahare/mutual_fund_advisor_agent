import os
import requests
from typing import Dict, Any
from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field
from datetime import date

# Constants
GEMINI_MODEL = "gemini-2.0-flash"
BASE_URL = os.getenv("MUTUAL_FUND_SERVER_BASE_URL")

# API functions
def create_user_api(name: str, email: str, password: str, phone_number: str) -> Dict[str, Any]:
    headers = {"Content-Type": "application/json"}
    payload = {
        "name": name,
        "email": email,
        "password": password,
        "phoneNumber": phone_number
    }
    response = requests.post(f"{BASE_URL}/users/register", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def login_investment_portal(email: str, password: str) -> Dict[str, Any]:
    headers = {"Content-Type": "application/json"}
    payload = {"email": email, "password": password}
    response = requests.post(f"{BASE_URL}/users/login", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def start_sip_api(fund_id: str, amount: float, frequency: str, deduction_day: int, start_date: str, end_date: str, jwt_token: str) -> Dict[str, Any]:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {jwt_token}"
    }
    payload = {
        "fundId": fund_id,
        "amount": amount,
        "frequency": frequency,
        "deductionDay": deduction_day,
        "startDate": start_date,
        "endDate": end_date
    }
    response = requests.post(f"{BASE_URL}/transactions/sip", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

# Output Schema
class InvestmentDetailsOutput(BaseModel):
    fund_id: str = Field(..., description="ID of the selected mutual fund")
    fund_name: str = Field(..., description="Name of the selected mutual fund")
    amount: float = Field(..., description="Monthly SIP investment amount")
    frequency: str = Field(default="Monthly", description="Frequency of SIP (Monthly by default)")
    deduction_day: int = Field(..., ge=1, le=31, description="Day of the month for SIP deduction")
    start_date: str = Field(..., description="SIP start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="SIP end date in YYYY-MM-DD format")

# Agent definition
investment_agent = LlmAgent(
    name="InvestmentAgent",
    model=GEMINI_MODEL,
    description="Handles the investment process after fund selection.",
    # output_schema=InvestmentDetailsOutput,
    instruction=f"""
          Role:
          - Guide the user through investing in a mutual fund via SIP (Systematic Investment Plan).

          1. Fund Validation:
            - Retrieve selected_fund from session state (recommended_funds.selected_fund).
            - If it's missing or has no _id, reply:
              "I notice there's an issue with the fund selection. Let me help you choose a fund again."
              - Set flow_stage = "funds_recommended"
              - Internally return control to FundRecommenderAgent

          2. Registration/Login Decision:
            - Ask: "Have you already registered on our investment portal, or would you like to create a new account?"
            - If user is already registered:
              * Ask for email and password.
              * Call login_investment_portal
              * Store: user_profile.email, jwt_token
            - If user is new:
              * Ask for name, email, password, and phone number
              * Call create_user_api
              * Store: user_profile.name, email, phone_number, jwt_token

          3. SIP Setup:
            - Confirm selected fund using recommended_funds.selected_fund.name, recommended_funds.selected_fund._id, and recommended_funds.selected_fund.min_sip_amount
            - Ask:
              * "What amount would you like to invest monthly? (Minimum ₹[min_sip_amount])"
              * "On which day of the month should the SIP be deducted? (1-31)"
              * "When would you like to end the SIP? (format: YYYY-MM-DD)"
            - Default start_date = today’s date in YYYY-MM-DD

          4. SIP Execution:
            - fund_id = recommended_funds.selected_fund._id (is the unique id of the fund selected by the user)
            - Call start_sip_api with:
              * fund_id, amount, frequency, deduction_day, start_date, end_date, jwt_token
            - Store investment_details in session:
              * amount, frequency, deduction_day, start_date, end_date

          5. Confirmation:
            - On success, respond:
              "✅ Your investment in [fund_name] has been set up!"
              "Monthly Amount: ₹[investment_details.amount], Deduction Day: [investment_details.deduction_day], Duration: [investment_details.start_date] to [investment_details.end_date]"
              "You're all set to grow your wealth! 🎉"
              - Set flow_stage = "investment_complete"

          Guidelines:
          - Collect the data by asking one question at a time and give options to choose from.
          - Ask Frequency question with ShowOption enabled
            - in a new line & give a options to choose from in new line.
            - eg. Frequency:
                - 1. Monthly
                - 2. Quarterly
                - 3. Yearly
          - Set/update the user input or answer in the format of InvestmentDetailsOutput one by one.
          - Always verify selected_fund before proceeding.
          - Always store and validate user/session data.
          - Never expose tool/internal names to the user.
          - Validate each user input (e.g., email format, password length, amount >= min_sip).
          - Use friendly and helpful tone throughout.
          - Do not show any other agent name or tool name to the user.
          - Do not tell user that you are forwarding the interaction to the **MutualFundAdvisorAgent** to handle the next step.
          - Do not show json format to the user.
          - After collecting the necessary information, return the Output in the format of InvestmentDetailsOutput.
          - After collecting the necessary information, smoothly forward the interaction to the **MutualFundAdvisorAgent** to handle the next step(this is mandatory to proceed further).
          
          Output Format:
          - Return information in summary format.
              - eg. InvestmentDetailsOutput:
                  - Fund ID: 1234567890
                  - Fund Name: Axis Small Cap Fund
                  - Amount: 10000
                  - Frequency: Monthly
                  - Deduction Day: 15
                  - Start Date: 2025-01-01
          """,
    output_key="investment_details",
    tools=[
        create_user_api,
        login_investment_portal,
        start_sip_api
    ],
)
