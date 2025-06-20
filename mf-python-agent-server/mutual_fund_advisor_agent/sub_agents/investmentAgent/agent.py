import os
import requests
from typing import Dict, Any
from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext

# Constants
GEMINI_MODEL = "gemini-2.0-flash"
BASE_URL = os.getenv("MUTUAL_FUND_SERVER_BASE_URL")

# API functions
def create_user_api(name: str, email: str, password: str, phone_number: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Create a new user in the investment portal."""
    headers = {"Content-Type": "application/json"}
    payload = {
        "name": name,
        "email": email,
        "password": password,
        "phoneNumber": phone_number
    }
    response = requests.post(f"{BASE_URL}/users/register", headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    if "user" in data:
        tool_context.state["user_registered"] = True
    else:
        tool_context.state["user_registered"] = False
    return {
        "action": "create_user_api",
        "data": data.get("user", None),
        "message": "User created successfully" if "user" in data else "User creation failed",
    }

def login_investment_portal(email: str, password: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Login to the investment portal."""
    headers = {"Content-Type": "application/json"}
    payload = {"email": email, "password": password}
    response = requests.post(f"{BASE_URL}/users/login", headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    if "user" in data and "token" in data:
        tool_context.state["user_registered"] = True
        tool_context.state["jwt_token"] = data["token"]
    else:
        tool_context.state["user_registered"] = False
        tool_context.state["jwt_token"] = None
    return {
        "action": "login_investment_portal",
        "data": data,
        "message": "Login successful" if "token" in data else "Login failed",
    }

def start_sip_api(fund_id: str, amount: float, frequency: str, deduction_day: int, start_date: str, end_date: str, jwt_token: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Start a SIP in the investment portal."""
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
    data = response.json()
    if "_id" in data:
        tool_context.state["sip_started"] = True
    else:
        tool_context.state["sip_started"] = False
    return {
        "action": "start_sip_api",
        "data": data,
        "message": "SIP started successfully" if "_id" in data else "SIP start failed",
    }

# Agent definition
investment_agent = LlmAgent(
    name="InvestmentAgent",
    model=GEMINI_MODEL,
    description="Handles the investment process after fund selection.",
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
            - Default start_date = today's date in YYYY-MM-DD

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
          
          Error Handling:
          - If Registration/Login fails, ask the user to try again.
          - In response of Register API, if user is already registered, ask the user to login.
          - In response of Login API, if user is not registered, ask the user to register.
          - In response of SIP API, if SIP start fails, ask the user to try again.
          """,
    tools=[
        create_user_api,
        login_investment_portal,
        start_sip_api
    ],
)
