# Schema Documentation

## Overview

The Mutual Fund Advisor application now uses a centralized schema system located in `mutual_fund_advisor_agent/schemas.py`. This ensures consistency across all sub-agents and makes the codebase more maintainable.

## Schema Structure

### 📁 File Location
```
mutual_fund_advisor_agent/
├── schemas.py                    # Centralized schemas
├── agent.py                      # Main agent
└── sub_agents/
    ├── userProfileAgent/
    │   └── agent.py             # Uses UserProfileOutput
    ├── investorClassifierAgent/
    │   └── agent.py             # Uses InvestorTypeOutput
    ├── goalPlannerAgent/
    │   └── agent.py             # Uses InvestmentGoalOutput
    ├── fundRecommenderAgent/
    │   ├── agent.py             # Uses FundRecommendationOutput
    │   └── validation_agent.py  # Uses FundValidationOutput
    ├── SIPCalculatorAgent/
    │   └── agent.py             # Uses SIPCalculatorOutput
    └── investmentAgent/
        └── agent.py             # Uses InvestmentDetailsOutput
```

## Available Schemas

### 🧑‍💼 User Profile Schemas

#### `UserProfileOutput`
Used by: `userProfileAgent`
```python
class UserProfileOutput(BaseModel):
    name: str                    # User's name
    age: int                     # User's age
    monthly_income: float        # Monthly income in INR
    assets: Optional[List[str]]  # Optional assets (FDs, gold, property)
    existing_investments: List[str]  # Current investments
    risk_tolerance: str          # Low, Medium, or High
    investment_horizon_years: int # Investment duration
    preferred_investment_mode: str # SIP, Lumpsum, or Hybrid
    investment_experience: str   # Beginner, Intermediate, or Advanced
```

### 📊 Investor Classification Schemas

#### `InvestorTypeOutput`
Used by: `investorClassifierAgent`
```python
class InvestorTypeOutput(BaseModel):
    investor_type: str           # Conservative, Balanced, or Aggressive
    investment_goal: str         # Primary investment goal
    risk_profile: str            # Detailed risk profile
    investment_strategy: str     # Recommended strategy
```

### 🎯 Goal Planning Schemas

#### `InvestmentGoalOutput`
Used by: `goalPlannerAgent`
```python
class InvestmentGoalOutput(BaseModel):
    goal_name: str               # Name of the goal
    time_horizon_years: int      # Investment duration
    target_amount: Optional[float] # Target amount (optional)
    monthly_investment_needed: Optional[float] # Monthly investment needed
    recommended_fund_type: List[str] # Suggested fund categories
    priority: str                # High, Medium, or Low
```

### 💰 Fund Recommendation Schemas

#### `FundReturn`
```python
class FundReturn(BaseModel):
    _1W: float                   # 1 Week return
    _1M: float                   # 1 Month return
    _3M: float                   # 3 Months return
    _6M: float                   # 6 Months return
    YTD: float                   # Year to Date return
    _1Y: float                   # 1 Year return
    _2Y: float                   # 2 Years return
    _3Y: float                   # 3 Years return
    _5Y: float                   # 5 Years return
    _10Y: float                  # 10 Years return
```

#### `RecommendedFund`
```python
class RecommendedFund(BaseModel):
    id: str                      # Fund ID
    name: str                    # Fund name
    risk_level: str              # Risk level
    fund_type: str               # Fund type
    category: str                # Fund category
    min_sip_amount: float        # Minimum SIP amount
    nav: float                   # Net Asset Value
    fund_size: float             # Fund size in crores
    is_active: bool              # Active status
    returns: FundReturn          # Returns data
    createdAt: datetime          # Creation date
    updatedAt: datetime          # Last update date
    recommendation_reason: str   # Why recommended
```

#### `FundRecommendationOutput`
Used by: `fundRecommenderAgent`
```python
class FundRecommendationOutput(BaseModel):
    recommended_funds: List[RecommendedFund]  # Top 2-3 funds
    selection_criteria: str      # Selection criteria used
    risk_alignment: str          # Risk alignment description
```

#### `FundValidationOutput`
Used by: `fundRecommenderAgent/validation_agent`
```python
class FundValidationOutput(BaseModel):
    new_funds: Optional[List[RecommendedFund]]  # New funds to show
    message: Optional[str]       # Message when no new funds
```

### 📈 SIP Calculator Schemas

#### `SIPCalculatorInput`
```python
class SIPCalculatorInput(BaseModel):
    monthly_amount: float        # Monthly SIP amount
    duration_years: int          # Investment duration
    expected_return_rate: float  # Expected annual return rate
    fund_id: Optional[str]       # Selected fund ID
```

#### `SIPCalculatorOutput`
Used by: `SIPCalculatorAgent`
```python
class SIPCalculatorOutput(BaseModel):
    sip_amount: float            # Monthly SIP amount
    sip_duration: int            # Duration in years
    total_investment: float      # Total amount invested
    expected_return: float       # Expected return amount
    total_value: float           # Total value at maturity
    wealth_gained: float         # Wealth gained
    return_rate_used: float      # Return rate used
```

### 💼 Investment Schemas

#### `InvestmentDetailsOutput`
Used by: `investmentAgent`
```python
class InvestmentDetailsOutput(BaseModel):
    fund_id: str                 # Selected fund ID
    fund_name: str               # Selected fund name
    amount: float                # Monthly SIP amount
    frequency: str               # SIP frequency
    deduction_day: int           # Deduction day (1-31)
    start_date: str              # Start date (YYYY-MM-DD)
    end_date: str                # End date (YYYY-MM-DD)
    user_email: Optional[str]    # User's email
    investment_status: str       # Investment status
```

### 🔄 Session State Schema

#### `SessionState`
Complete session state schema:
```python
class SessionState(BaseModel):
    user_profile: Optional[UserProfileOutput]
    investor_type: Optional[InvestorTypeOutput]
    investment_goal: Optional[InvestmentGoalOutput]
    fund_recommendations: Optional[FundRecommendationOutput]
    selected_fund: Optional[RecommendedFund]
    sip_calculator_output: Optional[SIPCalculatorOutput]
    investment_details: Optional[InvestmentDetailsOutput]
    flow_stage: str              # Current stage
    interaction_history: List[Dict[str, Any]]
```

### 🔧 Utility Schemas

#### `APIResponse`
Generic API response:
```python
class APIResponse(BaseModel):
    success: bool                # Operation success
    message: str                 # Response message
    data: Optional[Dict[str, Any]] # Response data
    error: Optional[str]         # Error message
```

#### `ValidationResult`
Validation results:
```python
class ValidationResult(BaseModel):
    is_valid: bool               # Validation passed
    errors: List[ValidationError] # Validation errors
    warnings: List[str]          # Validation warnings
```

## Usage Examples

### Importing Schemas in Sub-Agents

```python
# Before (old way)
from pydantic import BaseModel, Field
from typing import List, Optional

class UserProfileOutput(BaseModel):
    name: str = Field(..., description="Name of the user")
    # ... more fields

# After (new way)
from ..schemas import UserProfileOutput
```

### Using Schemas in Agent Definitions

```python
from google.adk.agents import LlmAgent
from ..schemas import UserProfileOutput

user_profile_agent = LlmAgent(
    name="UserProfileAgent",
    model="gemini-2.0-flash",
    description="Gathers user profile information",
    instruction="...",
    output_key="user_profile",
    # The schema is automatically used from the import
)
```

### Adding New Schemas

To add a new schema:

1. **Add to `schemas.py`**:
```python
class NewSchema(BaseModel):
    field1: str = Field(..., description="Description")
    field2: Optional[int] = Field(None, description="Optional field")
```

2. **Import in sub-agent**:
```python
from ..schemas import NewSchema
```

3. **Use in agent definition**:
```python
agent = LlmAgent(
    # ... other parameters
    output_key="new_output",
    # Schema is automatically used
)
```

## Benefits

### ✅ Consistency
- All sub-agents use the same data structures
- Consistent field names and types
- Standardized validation rules

### ✅ Maintainability
- Single source of truth for all schemas
- Easy to update field definitions
- Centralized documentation

### ✅ Type Safety
- Pydantic validation across all agents
- Better IDE support and autocomplete
- Runtime type checking

### ✅ Reusability
- Schemas can be shared between agents
- Common patterns are standardized
- Easy to extend and modify

## Migration Guide

If you have existing sub-agents with their own schemas:

1. **Move schema to `schemas.py`**
2. **Update imports in sub-agent**
3. **Remove local schema definitions**
4. **Test the agent functionality**

## Best Practices

1. **Always import from `schemas.py`** - Don't define schemas locally
2. **Use descriptive field names** - Make schemas self-documenting
3. **Add proper descriptions** - Help with agent instructions
4. **Use Optional for non-required fields** - Be explicit about requirements
5. **Keep schemas focused** - One schema per logical concept
6. **Update documentation** - Keep this file current with schema changes

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure the relative import path is correct
2. **Schema Mismatches**: Verify field names and types match between agents
3. **Validation Errors**: Check that all required fields are provided
4. **Circular Imports**: Avoid importing schemas in `schemas.py` itself

### Debug Tips

1. **Print schema structure**: `print(UserProfileOutput.schema())`
2. **Validate data**: `UserProfileOutput(**data)`
3. **Check field types**: `UserProfileOutput.__fields__` 