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

# Create the fund recommender agent
fund_recommender_agent = LlmAgent(
    name="FundRecommenderAgent",
    model=GEMINI_MODEL,
    description = "Suggests mutual funds tailored to the user's profile, investor type, and financial goals.",
    instruction = f"""
    Role:
    - Recommend mutual funds based on the user's risk profile, goals, and investment preferences.

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
    "Would you like to invest in any of these using SIP or lumpsum?"

    If YES:
    - Transfer control to the InvestmentAgent for handling the investment process

    Guidelines:
    - Maintain friendly, clear, and professional tone
    - Don't expose backend function names or internal logic
    - Validate all user inputs where needed (e.g., amount must be a number)
    - Use smart defaults (e.g., current date for start)
    - Continue supporting the user until they are done
    - End the session politely if the user has no more queries:
    - "Thanks again! We're here whenever you need personalized investment advice."
    """,
    output_key="fund_recommendation",
    tools=[fetch_funds_api, AgentTool(fund_validation_agent)],
)
