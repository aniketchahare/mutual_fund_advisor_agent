"""
Fund Recommender Agent

This agent is responsible for recommending appropriate mutual funds based on user profile,
investor classification, and investment goals, providing specific recommendations for SIP,
lumpsum investments, and tax-saving options.
"""

import os
from google.adk.agents import LlmAgent
import requests
from typing import List, Dict, Any
from google.adk.tools.agent_tool import AgentTool
from .validation_agent import fund_validation_agent

# --- Constants ---
GEMINI_MODEL = "gemini-2.0-flash"
BASE_URL = os.getenv("MUTUAL_FUND_SERVER_BASE_URL")

# Mutual Fund Schema
MUTUAL_FUND_SCHEMA = {
    "type": "object",
    "properties": {
        "_id": {"type": "string"},
        "name": {"type": "string", "description": "Fund Name"},
        "risk_level": {"type": "string", "description": "Risk Level (e.g., Very High, Moderate)"},
        "fund_type": {"type": "string", "description": "Type of Fund (e.g., Equity, Debt)"},
        "category": {"type": "string", "description": "Category (e.g., Sectoral, Large Cap)"},
        "min_sip_amount": {"type": "number", "description": "Minimum SIP Amount"},
        "nav": {"type": "number", "description": "Net Asset Value"},
        "fund_size": {"type": "number", "description": "Fund Size (in crores)"},
        "is_active": {"type": "boolean", "description": "Is the fund currently active?"},
        "returns": {
            "type": "object",
            "properties": {
                "1W": {"type": "number"},
                "1M": {"type": "number"},
                "3M": {"type": "number"},
                "6M": {"type": "number"},
                "YTD": {"type": "number"},
                "1Y": {"type": "number"},
                "2Y": {"type": "number"},
                "3Y": {"type": "number"},
                "5Y": {"type": "number"},
                "10Y": {"type": "number"}
            },
            "required": ["1W", "1M", "3M", "6M", "YTD", "1Y", "2Y", "3Y", "5Y", "10Y"]
        },
        "createdAt": {"type": "string", "format": "date-time"},
        "updatedAt": {"type": "string", "format": "date-time"}
    },
    "required": ["_id", "name", "risk_level", "fund_type", "category", "min_sip_amount", "nav", "fund_size", "is_active", "returns", "createdAt", "updatedAt"]
}

def fetch_funds_api() -> List[Dict[str, Any]]:
    """Fetch mutual funds from the local API and return the data as a list of dicts following the schema."""
    response = requests.get(f"{BASE_URL}/funds")
    response.raise_for_status()
    funds = response.json()
    # Optionally: Validate against schema here if needed
    return funds

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

def start_sip_api( fund_id: str, amount: float, frequency: str, deduction_day: int, start_date: str, end_date: str, jwt_token: str) -> Dict[str, Any]:
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

# Create the fund recommender agent
fund_recommender_agent = LlmAgent(
    name="FundRecommenderAgent",
    model=GEMINI_MODEL,
    description="Recommends personalized mutual fund investments based on user profile, investor type, and investment goals",
    instruction="""
    Role:
    - Suggest the best-fit mutual funds based on user type, goals, and risk.

    Instructions:
    - After collecting user profile, call the fetch_funds_api tool to retrieve and display available mutual funds to the user.
    - The mutual fund data will follow this schema:
    {MUTUAL_FUND_SCHEMA}
    - Track the IDs of mutual funds already shown to the user (e.g., in a variable called shown_fund_ids).
    - If the user asks for more mutual funds, call fetch_funds_api again, then use the fund_validation_agent tool with all_funds and shown_fund_ids. If fund_validation_agent responds with a message, show it to the user. If it returns new funds, display only the new ones and update shown_fund_ids.
    - Accept inputs:
        - Investor Type (Conservative, Balanced, Aggressive)
        - Investment Goals
        - Preferred Mode (SIP / Lumpsum)
    - Use logic to recommend:
        - Conservative: Short-term Debt, Liquid Funds
        - Balanced: Hybrid, Large-cap Equity Funds
        - Aggressive: Small-cap, Flexi-cap, Thematic Funds
    - Include 2–3 fund names per category.
    - Add reason for each suggestion (e.g., "Mirae Asset Emerging Bluechip Fund – good long-term performer for aggressive investors")
    - If the user asks for more details about a fund, provide the available information from the API response.
    - If the user asks for more mutual funds, call fetch_funds_api again, then use the fund_validation_agent tool with all_funds and shown_fund_ids. If fund_validation_agent responds with a message, show it to the user. If it returns new funds, display only the new ones and update shown_fund_ids.

    Note:
    - If user asks for calculation of the returns of the fund, then ask for the amount they want to invest in each month & transfer the conversation to the SIP calculator agent, if the user satisfies with the result, then the conversation will be transferred to the fundRecommenderAgent where it left the conversation.
    - The fund_validation_agent tool is a custom tool that validates the mutual funds and returns a list of new funds.
    - Keep the conversation going until the user is satisfied with the recommendations.
    - Once the user is satisfied, ask for the final confirmation to proceed with the investment to buy.
    - First ask user to login to the investment portal, if the user is not logged in, then ask for the email and password and call the login_investment_portal tool.
    - If login_investment_portal throws an error, then ask the user to check their credentials and try again or create a new account.
    - If user ask to create a new account, then ask for the name, email, password, phone number and call the create_user_api tool.
    - Once the user is logged in, then ask for which fund they want to invest in.
    - Once the fund is selected, ask for the mode of investment (SIP or lumpsum).
    - Once the mode is selected, ask for the amount they want to invest in each month.
    - Once the amount is entered, ask for the day(like 2, 25, 30...) of deduction of the amount in each month.
    - Once the day is entered, the default start date of the SIP is current date(do not ask to user to enter the start date).
    - Once the day is entered, ask for the end date of the SIP.
    - Once the end date is entered, call the start_sip_api tool to start the SIP.
    - Once recieved the response from the start_sip_api tool, show the user the details of the SIP(recieved from the start_sip_api tool) and ask for the confirmation to proceed.
    - Keep the conversation going, ask for futher queries or any other fund recommendations.
    - If the user asks for any other fund recommendations, call the fetch_funds_api tool again, then use the fund_validation_agent tool with all_funds and shown_fund_ids. If fund_validation_agent responds with a message, show it to the user. If it returns new funds, display only the new ones and update shown_fund_ids.
    - If no more fund recommendations are needed, then respond to the user with gratitude and ask them to come back if they need any more assistance.
    """.replace("{MUTUAL_FUND_SCHEMA}", str(MUTUAL_FUND_SCHEMA)),
    output_key="fund_recommendation",
    tools=[fetch_funds_api, AgentTool(fund_validation_agent), create_user_api, login_investment_portal, start_sip_api],
)
