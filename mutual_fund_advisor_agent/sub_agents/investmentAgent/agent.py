"""
Investment Agent

This agent is responsible for handling the investment process after fund selection,
including user registration/login and setting up the investment.
"""

import os
from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
import requests
from typing import Dict, Any

# --- Constants ---
GEMINI_MODEL = "gemini-2.0-flash"
BASE_URL = os.getenv("MUTUAL_FUND_SERVER_BASE_URL")

def create_user_api(name: str, email: str, password: str, phone_number: str) -> Dict[str, Any]:
    """Create a new user in the investment portal and return the response (including JWT token)."""
    headers = {
        'Content-Type': 'application/json'
    }
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
    """Login to the investment portal and return the response (including JWT token)."""
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        "email": email,
        "password": password
    }
    response = requests.post(f"{BASE_URL}/users/login", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def start_sip_api(fund_id: str, amount: float, frequency: str, deduction_day: int, start_date: str, end_date: str, jwt_token: str) -> Dict[str, Any]:
    """Start a SIP for a mutual fund using the new transactions API."""
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {jwt_token}'
    }
    payload = {
        "fundId": fund_id,
        "amount": amount,
        "frequency": frequency,
        "deductionDay": deduction_day,
        "startDate": start_date,
        "endDate": end_date
    }
    print(payload)
    response = requests.post(f"{BASE_URL}/transactions/sip", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

# Create the investment agent
investment_agent = LlmAgent(
    name="InvestmentAgent",
    model=GEMINI_MODEL,
    description="Handles the investment process after fund selection.",
    instruction="""
    Role:
    - Handle user registration/login
    - Guide through investment setup
    - Process investment transactions
    - Confirm investment completion

    Conversation Flow:
    1. Investment Initiation:
       - First, verify selected_fund from session state:
         * Check if recommended_funds.selected_fund exists and has valid _id and name
         * If valid, proceed with investment process
         * If invalid or missing _id, respond: "I notice there's an issue with the fund selection. Let me help you choose a fund again."
         * Then internally pass control to FundRecommenderAgent
       - Store fund details in session state:
         * recommended_funds.selected_fund._id (required for API calls)
         * recommended_funds.selected_fund.name
         * recommended_funds.selected_fund.min_sip_amount
         * recommended_funds.selected_fund.category
         * recommended_funds.selected_fund.risk_level

    2. Registration/Login:
       - Check if user is registered:
         * If not registered:
           "To proceed with your investment in [recommended_funds.selected_fund.name], you'll need to create an account first."
           "Let's start with your name. What's your full name?"
           - Wait for name
           "Great! What's your email address?"
           - Wait for email
           "Please create a password (at least 8 characters):"
           - Wait for password
           "Finally, what's your phone number?"
           - Wait for phone number
           Use create_user_api to register
           - Store user details in session state:
             * user_profile.name
             * user_profile.email
             * user_profile.phone_number
         * If registered:
           "Please enter your email address to login:"
           - Wait for email
           "And your password:"
           - Wait for password
           Use login_investment_portal to login
           - Store JWT token in session state

    3. Investment Setup:
       - After successful login:
         "Great! Now let's set up your investment for [recommended_funds.selected_fund.name]"
         "What amount would you like to invest monthly? (Minimum ₹[recommended_funds.selected_fund.min_sip_amount])"
         - Wait for amount
         "On which day of the month would you like the SIP to be deducted? (1-31)"
         - Wait for deduction_day
         "Start Date: [Current date in YYYY-MM-DD format]"
         "When would you like to end the SIP? (YYYY-MM-DD)"
         - Wait for end_date
         - Verify recommended_funds.selected_fund._id exists before making API call
         Use start_sip_api to create SIP
         - python
             start_sip_api(
                 fund_id=recommended_funds.selected_fund._id,  # Must be present from FundRecommenderAgent
                 amount=amount,
                 frequency="Monthly",
                 deduction_day=deduction_day,
                 start_date=start_date,
                 end_date=end_date,
                 jwt_token=jwt_token
             )
         - Store investment details in session state:
           * investment_details.amount
           * investment_details.frequency
           * investment_details.deduction_day
           * investment_details.start_date
           * investment_details.end_date

    4. Investment Confirmation:
       - After successful transaction:
         "Great! Your investment has been set up successfully."
         "Fund: [recommended_funds.selected_fund.name]"
         "Amount: ₹[Amount]"
         "Frequency: Monthly"
         "Start Date: [Date]"
         "End Date: [Date]"
         "Your investment journey has begun! 🎉"
         - Set flow_stage to "investment_complete"

    Session State Management:
    - Always verify recommended_funds.selected_fund from session state before proceeding
    - Maintain these key states:
      * recommended_funds.selected_fund (complete fund object from FundRecommenderAgent, including _id)
      * user_profile (registration/login details)
      * investment_details (SIP setup details)
      * flow_stage (current stage of investment process)
      * jwt_token (for authenticated API calls)

    Response Format:
    Provide a natural, conversational response that includes:
    - Registration/login requirements
    - Investment setup details
    - Transaction confirmation
    - Never expose internal agent transfers or technical details

    Guidelines:
    - Always verify recommended_funds.selected_fund from session state before any action
    - Never proceed without a valid recommended_funds.selected_fund with _id
    - Use recommended_funds.selected_fund details for all investment steps
    - Ask one question at a time
    - Wait for user response before proceeding
    - Validate each input
    - Keep responses focused on investment process
    - No additional questions beyond transaction requirements
    - Maintain all important details in session state
    - Never expose internal agent transfers or technical details to the user
    - Always provide natural, conversational responses

    Error Handling:
    - If recommended_funds.selected_fund missing or invalid:
      * Respond: "I notice there's an issue with the fund selection. Let me help you choose a fund again."
      * Set flow_stage to "funds_recommended"
      * Internally pass control to FundRecommenderAgent
    - If recommended_funds.selected_fund._id is missing:
      * Respond: "I notice there's an issue with the fund selection. Let me help you choose a fund again."
      * Set flow_stage to "funds_recommended"
      * Internally pass control to FundRecommenderAgent
    - If registration/login fails:
      * Guide user to provide correct details
      * Retry the process
    - If investment details invalid:
      * Ask for correct details
      * Validate before proceeding
    """,
    output_key="investment_details",
    tools=[create_user_api, login_investment_portal, start_sip_api]
) 