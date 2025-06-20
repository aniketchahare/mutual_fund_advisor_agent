"""
Centralized Pydantic schemas for the Mutual Fund Advisor application.

This file contains all the data models used across different sub-agents
to ensure consistency and maintainability.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal


# ===== USER PROFILE SCHEMAS =====

class UserProfileOutput(BaseModel):
    """Schema for user profile information collected by UserProfileAgent."""
    name: str = Field(..., description="Name of the user")
    age: int = Field(..., description="Age of the user")
    monthly_income: float = Field(..., description="User's monthly income in INR")
    assets: Optional[List[str]] = Field(None, description="Optional list of assets like FDs, gold, property")
    existing_investments: List[str] = Field(..., description="Existing investments like PPF, MF, stocks")
    risk_tolerance: str = Field(..., description="Risk appetite: Low, Medium, or High")
    investment_horizon_years: int = Field(..., description="Number of years user wants to stay invested")
    preferred_investment_mode: str = Field(..., description="SIP, Lumpsum, or Hybrid")
    investment_experience: str = Field(..., description="Beginner, Intermediate, or Advanced")


# ===== INVESTOR CLASSIFICATION SCHEMAS =====

class InvestorTypeOutput(BaseModel):
    """Schema for investor type classification by InvestorClassifierAgent."""
    investor_type: str = Field(..., description="Type of investor: Conservative, Balanced, or Aggressive")
    investment_goal: str = Field(..., description="Primary investment goal: Wealth Creation, Retirement, etc.")
    risk_profile: str = Field(..., description="Detailed risk profile description")
    investment_strategy: str = Field(..., description="Recommended investment strategy")


# ===== GOAL PLANNING SCHEMAS =====

class InvestmentGoalOutput(BaseModel):
    """Schema for investment goal planning by GoalPlannerAgent."""
    goal_name: str = Field(..., description="Name of the investment goal")
    time_horizon_years: int = Field(..., description="How many years the user plans to invest for this goal")
    target_amount: Optional[float] = Field(None, description="Target amount for the goal (optional)")
    monthly_investment_needed: Optional[float] = Field(None, description="Monthly investment needed to reach goal")
    recommended_fund_type: List[str] = Field(..., description="Suggested fund category based on goal and time horizon")
    priority: str = Field(..., description="Goal priority: High, Medium, or Low")


# ===== FUND RECOMMENDATION SCHEMAS =====

class FundReturn(BaseModel):
    """Schema for mutual fund returns data."""
    W_1: float = Field(..., description="1 Week return")
    M_1: float = Field(..., description="1 Month return")
    M_3: float = Field(..., description="3 Months return")
    M_6: float = Field(..., description="6 Months return")
    YTD: float = Field(..., description="Year to Date return")
    Y_1: float = Field(..., description="1 Year return")
    Y_2: float = Field(..., description="2 Years return")
    Y_3: float = Field(..., description="3 Years return")
    Y_5: float = Field(..., description="5 Years return")
    Y_10: float = Field(..., description="10 Years return")


class RecommendedFund(BaseModel):
    """Schema for a recommended mutual fund."""
    id: str = Field(..., alias="_id", description="Unique fund identifier")
    name: str = Field(..., description="Name of the mutual fund")
    risk_level: str = Field(..., description="Risk level: Low, Medium, or High")
    fund_type: str = Field(..., description="Type of fund: Equity, Debt, Hybrid, etc.")
    category: str = Field(..., description="Fund category: Large Cap, Small Cap, etc.")
    min_sip_amount: float = Field(..., description="Minimum SIP amount")
    nav: float = Field(..., description="Net Asset Value")
    fund_size: float = Field(..., description="Fund size in crores")
    is_active: bool = Field(..., description="Whether the fund is active")
    returns: FundReturn = Field(..., description="Fund returns data")
    createdAt: str = Field(..., description="Fund creation date in ISO format")
    updatedAt: str = Field(..., description="Fund last update date in ISO format")
    recommendation_reason: str = Field(..., description="Why this fund was recommended")


class FundRecommendationOutput(BaseModel):
    """Schema for fund recommendations by FundRecommenderAgent."""
    recommended_funds: List[RecommendedFund] = Field(..., description="Top 2–3 funds recommended to the user")
    selection_criteria: str = Field(..., description="Criteria used for fund selection")
    risk_alignment: str = Field(..., description="How the recommendations align with user's risk profile")


class FundValidationOutput(BaseModel):
    """Schema for fund validation results."""
    new_funds: Optional[List[RecommendedFund]] = Field(
        default=None,
        description="List of mutual funds not yet shown to the user"
    )
    message: Optional[str] = Field(
        default=None,
        description="Message when no new funds are available"
    )


# ===== SIP CALCULATOR SCHEMAS =====

class SIPCalculatorInput(BaseModel):
    """Schema for SIP calculator input parameters."""
    monthly_amount: float = Field(..., description="Monthly SIP amount")
    duration_years: int = Field(..., description="Investment duration in years")
    expected_return_rate: float = Field(default=12.0, description="Expected annual return rate (%)")
    fund_id: Optional[str] = Field(None, description="Selected fund ID")


class SIPCalculatorOutput(BaseModel):
    """Schema for SIP calculator results."""
    sip_amount: float = Field(..., description="Monthly SIP amount")
    sip_duration: int = Field(..., description="Duration in years")
    total_investment: float = Field(..., description="Total amount invested")
    expected_return: float = Field(..., description="Expected return amount")
    total_value: float = Field(..., description="Total value at maturity")
    wealth_gained: float = Field(..., description="Wealth gained through investment")
    return_rate_used: float = Field(..., description="Return rate used for calculation")


# ===== INVESTMENT SCHEMAS =====

class InvestmentDetailsOutput(BaseModel):
    """Schema for investment details by InvestmentAgent."""
    fund_id: str = Field(..., description="ID of the selected mutual fund")
    fund_name: str = Field(..., description="Name of the selected mutual fund")
    amount: float = Field(..., description="Monthly SIP investment amount")
    frequency: str = Field(default="Monthly", description="Frequency of SIP (Monthly by default)")
    deduction_day: int = Field(..., ge=1, le=31, description="Day of the month for SIP deduction")
    start_date: str = Field(..., description="SIP start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="SIP end date in YYYY-MM-DD format")
    user_email: Optional[str] = Field(None, description="User's email for investment portal")
    investment_status: str = Field(default="Pending", description="Status of the investment setup")


# ===== SESSION STATE SCHEMAS =====

class SessionState(BaseModel):
    """Schema for complete session state."""
    user_profile: Optional[UserProfileOutput] = Field(None, description="User profile information")
    investor_type: Optional[InvestorTypeOutput] = Field(None, description="Investor classification")
    investment_goal: Optional[InvestmentGoalOutput] = Field(None, description="Investment goal details")
    fund_recommendations: Optional[FundRecommendationOutput] = Field(None, description="Fund recommendations")
    selected_fund: Optional[RecommendedFund] = Field(None, description="User's selected fund")
    sip_calculator_output: Optional[SIPCalculatorOutput] = Field(None, description="SIP calculation results")
    investment_details: Optional[InvestmentDetailsOutput] = Field(None, description="Investment setup details")
    user_registered: bool = Field(default=False, description="Whether the user is registered")
    jwt_token: Optional[str] = Field(None, description="JWT token for the user")
    sip_started: bool = Field(default=False, description="Whether the SIP is started")
    flow_stage: str = Field(default="initial", description="Current stage in the investment flow")
    interaction_history: List[Dict[str, Any]] = Field(default_factory=list, description="Conversation history")


# ===== API RESPONSE SCHEMAS =====

class APIResponse(BaseModel):
    """Generic API response schema."""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if any")


class FundAPIResponse(BaseModel):
    """Schema for fund API responses."""
    funds: List[RecommendedFund] = Field(..., description="List of mutual funds")
    total_count: int = Field(..., description="Total number of funds")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Number of funds per page")


# ===== VALIDATION SCHEMAS =====

class ValidationError(BaseModel):
    """Schema for validation errors."""
    field: str = Field(..., description="Field that failed validation")
    message: str = Field(..., description="Validation error message")
    value: Any = Field(..., description="Value that failed validation")


class ValidationResult(BaseModel):
    """Schema for validation results."""
    is_valid: bool = Field(..., description="Whether the validation passed")
    errors: List[ValidationError] = Field(default_factory=list, description="List of validation errors")
    warnings: List[str] = Field(default_factory=list, description="List of validation warnings")


# ===== UTILITY SCHEMAS =====

class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: str = Field(..., description="Error timestamp")


class SuccessResponse(BaseModel):
    """Schema for success responses."""
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    timestamp: str = Field(..., description="Response timestamp") 