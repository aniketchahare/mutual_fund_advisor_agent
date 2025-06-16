"""
Standardized output formats for all agents in the Mutual Fund Advisor system.
These formats ensure consistent state management and data exchange between agents.
"""

from typing import Dict, Any, List, Optional
from enum import Enum

class AgentStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    IN_PROGRESS = "in_progress"
    VALIDATION_ERROR = "validation_error"
    INCOMPLETE = "incomplete"

class ValidationError(Exception):
    """Custom exception for validation errors in agent responses."""
    pass

# Base format for all agent responses
class AgentResponse:
    def __init__(
        self,
        agent_name: str,
        status: str,
        message: str,
        data: Dict[str, Any],
        next_expected_input: Optional[str] = None,
        error: Optional[str] = None
    ):
        self.agent_name = agent_name
        self.status = self._validate_status(status)
        self.message = self._validate_message(message)
        self.data = self._validate_data(data)
        self.next_expected_input = next_expected_input
        self.error = error

    def _validate_status(self, status: str) -> str:
        """Validate the status field."""
        try:
            return AgentStatus(status).value
        except ValueError:
            raise ValidationError(f"Invalid status: {status}. Must be one of {[s.value for s in AgentStatus]}")

    def _validate_message(self, message: str) -> str:
        """Validate the message field."""
        if not isinstance(message, str):
            raise ValidationError("Message must be a string")
        if not message.strip():
            raise ValidationError("Message cannot be empty")
        return message

    def _validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the data field."""
        if not isinstance(data, dict):
            raise ValidationError("Data must be a dictionary")
        if not data:
            raise ValidationError("Data cannot be empty")
        return data

    def to_dict(self) -> Dict[str, Any]:
        """Convert the response to a dictionary format."""
        return {
            "agent_name": self.agent_name,
            "status": self.status,
            "message": self.message,
            "data": self.data,
            "next_expected_input": self.next_expected_input,
            "error": self.error
        }

    def to_user_message(self) -> str:
        """Convert the response to a user-friendly message."""
        if self.status == AgentStatus.ERROR.value:
            return f"I apologize, but I encountered an error: {self.error}"
        elif self.status == AgentStatus.VALIDATION_ERROR.value:
            return f"I need some clarification: {self.error}"
        elif self.status == AgentStatus.INCOMPLETE.value:
            return f"I need more information: {self.error}"
        else:
            return self.message

# User Profile Agent Output Format
class UserProfileOutput:
    @staticmethod
    def format(
        name: str,
        age: int,
        gender: str,
        monthly_income: float,
        investment_experience: str,
        message: str,
        status: str = "success",
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        # Validate inputs
        if not name or not isinstance(name, str):
            raise ValidationError("Name must be a non-empty string")
        if not isinstance(age, int) or age < 18 or age > 100:
            raise ValidationError("Age must be between 18 and 100")
        if not isinstance(monthly_income, (int, float)) or monthly_income <= 0:
            raise ValidationError("Monthly income must be a positive number")
        if investment_experience not in ["Beginner", "Intermediate", "Advanced"]:
            raise ValidationError("Investment experience must be one of: Beginner, Intermediate, Advanced")

        return AgentResponse(
            agent_name="UserProfileAgent",
            status=status,
            message=message,
            data={
                "user_profile": {
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "monthly_income": monthly_income,
                    "investment_experience": investment_experience
                }
            },
            next_expected_input="risk_assessment",
            error=error
        ).to_dict()

# Investor Classifier Agent Output Format
class InvestorClassifierOutput:
    @staticmethod
    def format(
        investor_type: str,
        risk_tolerance_score: float,
        message: str,
        status: str = "success",
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        # Validate inputs
        if investor_type not in ["Conservative", "Balanced", "Aggressive"]:
            raise ValidationError("Investor type must be one of: Conservative, Balanced, Aggressive")
        if not isinstance(risk_tolerance_score, (int, float)) or risk_tolerance_score < 0 or risk_tolerance_score > 100:
            raise ValidationError("Risk tolerance score must be between 0 and 100")

        return AgentResponse(
            agent_name="InvestorClassifierAgent",
            status=status,
            message=message,
            data={
                "investor_classification": {
                    "type": investor_type,
                    "risk_tolerance_score": risk_tolerance_score
                }
            },
            next_expected_input="investment_goal",
            error=error
        ).to_dict()

# Goal Planner Agent Output Format
class GoalPlannerOutput:
    @staticmethod
    def format(
        goal_type: str,
        target_amount: float,
        time_horizon_years: int,
        monthly_sip_target: float,
        message: str,
        status: str = "success",
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        # Validate inputs
        if goal_type not in ["Retirement", "Education", "Wealth Creation", "House Purchase"]:
            raise ValidationError("Invalid goal type")
        if not isinstance(target_amount, (int, float)) or target_amount <= 0:
            raise ValidationError("Target amount must be a positive number")
        if not isinstance(time_horizon_years, int) or time_horizon_years <= 0:
            raise ValidationError("Time horizon must be a positive number of years")
        if not isinstance(monthly_sip_target, (int, float)) or monthly_sip_target <= 0:
            raise ValidationError("Monthly SIP target must be a positive number")

        return AgentResponse(
            agent_name="GoalPlannerAgent",
            status=status,
            message=message,
            data={
                "investment_goal": {
                    "goal_type": goal_type,
                    "target_amount": target_amount,
                    "time_horizon_years": time_horizon_years,
                    "monthly_sip_target": monthly_sip_target
                }
            },
            next_expected_input="fund_selection",
            error=error
        ).to_dict()

# Fund Recommender Agent Output Format
class FundRecommenderOutput:
    @staticmethod
    def format(
        recommendations: List[Dict[str, Any]],
        message: str,
        selected_fund: Optional[Dict[str, Any]] = None,
        status: str = "success",
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        # Validate inputs
        if not isinstance(recommendations, list):
            raise ValidationError("Recommendations must be a list")
        if not recommendations:
            raise ValidationError("At least one fund recommendation is required")
        for fund in recommendations:
            if not isinstance(fund, dict):
                raise ValidationError("Each fund must be a dictionary")
            if "fund_id" not in fund or "name" not in fund:
                raise ValidationError("Each fund must have fund_id and name")

        return AgentResponse(
            agent_name="FundRecommenderAgent",
            status=status,
            message=message,
            data={
                "fund_recommendations": recommendations,
                "selected_fund": selected_fund or {}
            },
            next_expected_input="investment_setup" if selected_fund else "fund_selection",
            error=error
        ).to_dict()

# SIP Calculator Agent Output Format
class SIPCalculatorOutput:
    @staticmethod
    def format(
        monthly_investment: float,
        duration_years: int,
        expected_return_rate: float,
        total_investment: float,
        estimated_maturity_value: float,
        estimated_returns: float,
        message: str,
        status: str = "success",
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        # Validate inputs
        if not isinstance(monthly_investment, (int, float)) or monthly_investment <= 0:
            raise ValidationError("Monthly investment must be a positive number")
        if not isinstance(duration_years, int) or duration_years <= 0:
            raise ValidationError("Duration must be a positive number of years")
        if not isinstance(expected_return_rate, (int, float)) or expected_return_rate <= 0:
            raise ValidationError("Expected return rate must be a positive number")
        if not isinstance(total_investment, (int, float)) or total_investment <= 0:
            raise ValidationError("Total investment must be a positive number")
        if not isinstance(estimated_maturity_value, (int, float)) or estimated_maturity_value <= 0:
            raise ValidationError("Estimated maturity value must be a positive number")
        if not isinstance(estimated_returns, (int, float)) or estimated_returns < 0:
            raise ValidationError("Estimated returns must be a non-negative number")

        return AgentResponse(
            agent_name="SIPCalculatorAgent",
            status=status,
            message=message,
            data={
                "sip_calculation": {
                    "monthly_investment": monthly_investment,
                    "duration_years": duration_years,
                    "expected_return_rate": expected_return_rate,
                    "total_investment": total_investment,
                    "estimated_maturity_value": estimated_maturity_value,
                    "estimated_returns": estimated_returns
                }
            },
            next_expected_input="fund_selection",
            error=error
        ).to_dict()

# Investment Agent Output Format
class InvestmentOutput:
    @staticmethod
    def format(
        user_account_created: bool,
        logged_in_investment_portal: bool,
        sip_initiated: bool,
        sip_transaction_id: Optional[str] = None,
        status: str = "success",
        error: Optional[str] = None,
        message: str = ""
    ) -> Dict[str, Any]:
        # Validate inputs
        if not isinstance(user_account_created, bool):
            raise ValidationError("user_account_created must be a boolean")
        if not isinstance(logged_in_investment_portal, bool):
            raise ValidationError("logged_in_investment_portal must be a boolean")
        if not isinstance(sip_initiated, bool):
            raise ValidationError("sip_initiated must be a boolean")
        if sip_initiated and not sip_transaction_id:
            raise ValidationError("sip_transaction_id is required when sip_initiated is True")

        return AgentResponse(
            agent_name="InvestmentAgent",
            status=status,
            message=message,
            data={
                "investment_status": {
                    "user_account_created": user_account_created,
                    "logged_in_investment_portal": logged_in_investment_portal,
                    "sip_initiated": sip_initiated,
                    "sip_transaction_id": sip_transaction_id
                }
            },
            next_expected_input="confirmation" if sip_initiated else "investment_setup",
            error=error
        ).to_dict()

# Root Agent Output Format
class RootAgentOutput:
    @staticmethod
    def format(
        current_agent: str,
        previous_agent: Optional[str],
        next_expected_input: str,
        last_agent_response: str,
        message: str,
        status: str = "success",
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        # Validate inputs
        valid_agents = [
            "MutualFundAdvisorAgent",
            "UserProfileAgent",
            "InvestorClassifierAgent",
            "GoalPlannerAgent",
            "FundRecommenderAgent",
            "SIPCalculatorAgent",
            "InvestmentAgent"
        ]
        if current_agent not in valid_agents:
            raise ValidationError(f"Invalid current_agent. Must be one of: {valid_agents}")
        if previous_agent and previous_agent not in valid_agents:
            raise ValidationError(f"Invalid previous_agent. Must be one of: {valid_agents}")

        return AgentResponse(
            agent_name="MutualFundAdvisorAgent",
            status=status,
            message=message,
            data={
                "current_agent_status": {
                    "current_agent": current_agent,
                    "previous_agent": previous_agent,
                    "next_expected_input": next_expected_input,
                    "last_agent_response": last_agent_response
                }
            },
            next_expected_input=next_expected_input,
            error=error
        ).to_dict() 