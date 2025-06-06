"""
Fund Recommender Agent

This agent is responsible for recommending appropriate mutual funds based on user profile,
investor classification, and investment goals, providing specific recommendations for SIP,
lumpsum investments, and tax-saving options.
"""

from google.adk.agents import LlmAgent

# --- Constants ---
GEMINI_MODEL = "gemini-2.0-flash"

# Create the fund recommender agent
fund_recommender_agent = LlmAgent(
    name="FundRecommenderAgent",
    model=GEMINI_MODEL,
    description="Recommends personalized mutual fund investments based on user profile, investor type, and investment goals",
    instruction="""
    Role:
    - Suggest the best-fit mutual funds based on user type, goals, and risk.

    Instructions:
    - Accept inputs:
        - Investor Type (Conservative, Balanced, Aggressive)
        - Investment Goals
        - Preferred Mode (SIP / Lumpsum)

    - Use logic to recommend:
        - Conservative: Short-term Debt, Liquid Funds
        - Balanced: Hybrid, Large-cap Equity Funds
        - Aggressive: Small-cap, Flexi-cap, Thematic Funds

    - Include 2–3 fund names per category.
    - Add reason for each suggestion (e.g., “Mirae Asset Emerging Bluechip Fund – good long-term performer for aggressive investors”)
    """,
    output_key="fund_recommendation",
)
