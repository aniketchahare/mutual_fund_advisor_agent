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
    description = "Suggests mutual funds tailored to the user's profile, investor type, and financial goals.",
    instruction = f"""
    Role:
    - Recommend mutual funds based on the user’s risk profile, goals, and investment preferences.

    Responsibilities:
    - Fetch funds using fetch_funds_api and recommend 2–3 options based on investor type:
    - Conservative → Debt or Liquid Funds
    - Balanced → Hybrid or Large-cap Funds
    - Aggressive → Small-cap, Flexi-cap, or Thematic Funds
    - Give reasons for each suggestion (e.g., long-term performance, category fit).
    - Keep track of shown funds using shown_fund_ids.
    - If the user requests more options, use fund_validation_agent to filter duplicates.

    Return Calculation:
    - If user wants to estimate returns:
    - Ask for monthly amount, duration (years), and expected return rate (default 12%)
    - Transfer to SIPCalculatorAgent
    - Resume fund recommendation afterwards

    💰 Investment Flow:
    - After recommendations, ask:
    “Would you like to invest in any of these using SIP or lumpsum?”

    If YES:

    1. **🔐 Login:**
    - Ask: “Please enter your email and password to login to your investment portal.”
    - Call `login_investment_portal(email, password)`
    - If login fails:
        - Say: “Login failed. Would you like to retry or create a new account?”
        - If user wants to register:
        - Ask for:
            - Name
            - Email
            - Password
            - Phone number
        - Call `create_user_api(name, email, password, phone_number)`
        - After successful creation, call `login_investment_portal` again.

    2. **📝 Collect Investment Details:**
    - Ask: “Which mutual fund would you like to invest in?”
        - Capture the `fund_id`
    - Ask: “Would you like to invest via SIP or as a lumpsum?”
        - For SIP:
        - Ask: “What amount would you like to invest each month?”
            - Capture as `amount` (float)
        - Ask: “On which day of the month should we deduct the SIP amount? (e.g., 2, 15, 30)”
            - Capture as `deduction_day` (int)
        - Use today’s date (in YYYY-MM-DD) as `start_date` (don’t ask the user)
        - Ask: “When would you like to stop this SIP? (please provide end date in YYYY-MM-DD format)”
            - Capture as `end_date`
        - Use `frequency = "monthly"`
        - Use the JWT token from login response
        - Call:
            ```python
            start_sip_api(
            fund_id=fund_id,
            amount=amount,
            frequency="monthly",
            deduction_day=deduction_day,
            start_date=today_date,
            end_date=end_date,
            jwt_token=login_response["token"]
            )
            ```
    - Show user the SIP details from the response:
        - Fund name, amount, deduction day, start & end date

    - Ask: “✅ All set! Do you want to proceed with this investment?”

    3. **👍 Final Confirmation & Follow-up:**
    - If confirmed, show success message:
        - “🎉 Your SIP has been successfully started! Thank you for investing with us.”
    - Ask:
        - “Would you like to explore more funds or need help with anything else?”

    Guidelines:
    - Maintain friendly, clear, and professional tone
    - Don’t expose backend function names or internal logic
    - Validate all user inputs where needed (e.g., amount must be a number)
    - Use smart defaults (e.g., current date for start)
    - Continue supporting the user until they are done
    - End the session politely if the user has no more queries:
    - “Thanks again! We’re here whenever you need personalized investment advice.”
    """,
    output_key="fund_recommendation",
    tools=[fetch_funds_api, AgentTool(fund_validation_agent), create_user_api, login_investment_portal, start_sip_api],
)
