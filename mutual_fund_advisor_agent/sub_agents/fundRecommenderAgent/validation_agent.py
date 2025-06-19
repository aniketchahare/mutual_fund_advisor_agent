from google.adk.agents import LlmAgent

GEMINI_MODEL = "gemini-2.0-flash"

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
)
