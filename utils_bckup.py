from datetime import datetime
import asyncio
import logging
from typing import Dict, Any, Optional
from mutual_fund_advisor_agent.output_formats import ValidationError, AgentStatus

from google.genai import types


# ANSI color codes for terminal output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


def update_interaction_history(session_service, app_name, user_id, session_id, entry):
    """Add an entry to the interaction history in state.

    Args:
        session_service: The session service instance
        app_name: The application name
        user_id: The user ID
        session_id: The session ID
        entry: A dictionary containing the interaction data
            - requires 'action' key (e.g., 'user_query', 'agent_response')
            - other keys are flexible depending on the action type
    """
    try:
        # Get current session
        session = session_service.get_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )
        if not session:
            raise Exception(f"Session not found: {session_id}")

        # Get current state
        current_state = session.state.copy()
        
        # Get current interaction history
        interaction_history = current_state.get("interaction_history", [])

        # Add timestamp if not already present
        if "timestamp" not in entry:
            entry["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Add the entry to interaction history
        interaction_history.append(entry)

        # Update state with new interaction history
        current_state["interaction_history"] = interaction_history

        # Update the session with new state
        session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            state=current_state,
        )
    except Exception as e:
        print(f"Error updating interaction history: {e}")
        raise  # Re-raise the exception to handle it in the calling function


def add_user_query_to_history(session_service, app_name, user_id, session_id, query):
    """Add a user query to the interaction history."""
    update_interaction_history(
        session_service,
        app_name,
        user_id,
        session_id,
        {
            "action": "user_query",
            "query": query,
        },
    )


def add_agent_response_to_history(
    session_service, app_name, user_id, session_id, agent_name, response
):
    """Add an agent response to the interaction history."""
    update_interaction_history(
        session_service,
        app_name,
        user_id,
        session_id,
        {
            "action": "agent_response",
            "agent": agent_name,
            "response": response,
        },
    )


def display_state(
    session_service, app_name, user_id, session_id, label="Current State"
):
    """Display the current session state in a formatted way, reflecting the updated structure."""
    try:
        session = session_service.get_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )

        # Format the output with clear sections
        print(f"\n{'-' * 10} {label} {'-' * 10}")

        # Handle user profile information
        user_profile = session.state.get("user_profile", {})
        if user_profile:
            print(f"{Colors.BOLD}👤 User Profile:{Colors.RESET}")
            print(f"  Name: {user_profile.get('name', 'Not provided')}")
            print(f"  Age: {user_profile.get('age', 'Not provided')}")
            print(f"  Gender: {user_profile.get('gender', 'Not provided')}")
            print(f"  Monthly Income: {user_profile.get('monthly_income', 'Not provided')}")
            print(f"  Investment Experience: {user_profile.get('investment_experience', 'Not provided')}")

        # --- Updated Investment Details Section ---
        print(f"\n{Colors.BOLD}💰 Investment Details:{Colors.RESET}")

        investor_classification = session.state.get("investor_classification", {})
        if investor_classification:
            print(f"  {Colors.BOLD}Investor Classification:{Colors.RESET}")
            print(f"    Type: {investor_classification.get('type', 'Not determined')}")
            print(f"    Risk Tolerance Score: {investor_classification.get('risk_tolerance_score', 'Not assessed')}")

        investment_goal = session.state.get("investment_goal", {})
        if investment_goal:
            print(f"  {Colors.BOLD}Investment Goal:{Colors.RESET}")
            print(f"    Goal Type: {investment_goal.get('goal_type', 'Not set')}")
            print(f"    Target Amount: {investment_goal.get('target_amount', 'Not set')}")
            print(f"    Time Horizon (Years): {investment_goal.get('time_horizon_years', 'Not specified')}")
            print(f"    Monthly SIP Target: {investment_goal.get('monthly_sip_target', 'Not calculated')}")

        fund_recommendations = session.state.get("fund_recommendations", [])
        if fund_recommendations:
            print(f"  {Colors.BOLD}Fund Recommendations:{Colors.RESET}")
            for idx, fund in enumerate(fund_recommendations, 1):
                print(f"    {idx}. Fund Name: {fund.get('name', 'N/A')}")
                print(f"       Fund ID: {fund.get('fund_id', 'N/A')}")
                print(f"       Category: {fund.get('category', 'N/A')}")
                print(f"       Risk Level: {fund.get('risk_level', 'N/A')}")
                # Add more fund details as needed
        else:
            print(f"  Fund Recommendations: None")

        selected_fund = session.state.get("selected_fund", {})
        if selected_fund and selected_fund.get("fund_id"):
            print(f"  {Colors.BOLD}Selected Fund:{Colors.RESET}")
            print(f"    Name: {selected_fund.get('name', 'N/A')}")
            print(f"    ID: {selected_fund.get('fund_id', 'N/A')}")
        else:
            print(f"  Selected Fund: None")
            
        investment_status = session.state.get("investment_status", {})
        if investment_status:
            print(f"  {Colors.BOLD}Investment Status:{Colors.RESET}")
            print(f"    User Account Created: {investment_status.get('user_account_created', 'N/A')}")
            print(f"    Logged In Investment Portal: {investment_status.get('logged_in_investment_portal', 'N/A')}")
            print(f"    SIP Initiated: {investment_status.get('sip_initiated', 'N/A')}")
            print(f"    SIP Transaction ID: {investment_status.get('sip_transaction_id', 'N/A')}")


        current_agent_status = session.state.get("current_agent_status", {})
        if current_agent_status:
            print(f"  {Colors.BOLD}Current Agent Status:{Colors.RESET}")
            print(f"    Current Agent: {current_agent_status.get('current_agent', 'N/A')}")
            print(f"    Next Expected Input: {current_agent_status.get('next_expected_input', 'N/A')}")
            print(f"    Last Agent Response: {current_agent_status.get('last_agent_response', 'N/A')}")
        
        # --- End of Updated Investment Details Section ---

        # Handle interaction history in a more readable way
        interaction_history = session.state.get("interaction_history", [])
        if interaction_history:
            print(f"\n{Colors.BOLD}📝 Interaction History:{Colors.RESET}")
            for idx, interaction in enumerate(interaction_history, 1):
                if isinstance(interaction, dict):
                    action = interaction.get("action", "interaction")
                    timestamp = interaction.get("timestamp", "unknown time")

                    if action == "user_query":
                        query = interaction.get("query", "")
                        print(f'  {idx}. User query at {timestamp}: "{query}"')
                    elif action == "agent_response":
                        agent = interaction.get("agent", "unknown")
                        response = interaction.get("response", "")
                        # Truncate very long responses for display
                        if len(response) > 100:
                            response = response[:97] + "..."
                        print(f'  {idx}. {agent} response at {timestamp}: "{response}"')
                    else:
                        details = ", ".join(
                            f"{k}: {v}"
                            for k, v in interaction.items()
                            if k not in ["action", "timestamp"]
                        )
                        print(
                            f"  {idx}. {action} at {timestamp}"
                            + (f" ({details})" if details else "")
                        )
                else:
                    print(f"  {idx}. {interaction}")
        else:
            print(f"\n{Colors.BOLD}📝 Interaction History: None{Colors.RESET}")

        # Show any additional state keys that might exist
        # Exclude all known top-level keys
        known_keys = [
            "user_profile",
            "investor_classification",
            "investment_goal",
            "fund_recommendations",
            "selected_fund",
            "investment_status",
            "current_agent_status",
            "interaction_history"
        ]
        other_keys = [k for k in session.state.keys() if k not in known_keys]

        if other_keys:
            print(f"\n{Colors.BOLD}🔑 Additional State (Other Keys):{Colors.RESET}")
            for key in other_keys:
                print(f"  {key}: {session.state[key]}")

        print("-" * (22 + len(label)))
    except Exception as e:
        print(f"Error displaying state: {e}")


async def process_agent_response(event):
    """Process and display agent response events."""
    print(f"Event ID: {event.id}, Author: {event.author}")

    # Check for specific parts first
    has_specific_part = False
    if event.content and event.content.parts:
        for part in event.content.parts:
            if hasattr(part, "text") and part.text and not part.text.isspace():
                print(f"  Text: '{part.text.strip()}'")
                has_specific_part = True # Indicate that some text was printed

    # Check for final response after specific parts
    final_response = None
    # Only print final response if no specific parts were already printed to avoid duplication
    if not has_specific_part and event.is_final_response():
        if (
            event.content
            and event.content.parts
            and hasattr(event.content.parts[0], "text")
            and event.content.parts[0].text
        ):
            final_response = event.content.parts[0].text.strip()
            # Use colors and formatting to make the final response stand out
            print(
                f"\n{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD}╔══ AGENT RESPONSE ═════════════════════════════════════════{Colors.RESET}"
            )
            print(f"{Colors.CYAN}{Colors.BOLD}{final_response}{Colors.RESET}")
            print(
                f"{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD}╚═════════════════════════════════════════════════════════════{Colors.RESET}\n"
            )
        else:
            print(
                f"\n{Colors.BG_RED}{Colors.WHITE}{Colors.BOLD}==> Final Agent Response: [No text content in final event]{Colors.RESET}\n"
            )

    return final_response


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def call_agent_async(
    runner,
    user_id: str,
    session_id: str,
    message: str
) -> Dict[str, Any]:
    """
    Asynchronously call an agent and handle its response.
    
    Args:
        runner: The runner instance containing the agent and session service
        user_id: The user ID
        session_id: The current session ID
        message: The user's message
        
    Returns:
        Dict containing the agent's response and updated session state
    """
    try:
        # Get current session state
        current_session = runner.session_service.get_session(
            app_name=runner.app_name,
            user_id=user_id,
            session_id=session_id
        )
        if not current_session:
            raise ValueError(f"Session {session_id} not found")

        # Create a copy of the current state to avoid modifying the original
        current_state = current_session.state.copy()
        
        # Initialize or update current_agent_status
        current_state["current_agent_status"] = current_state.get("current_agent_status", {})
        current_state["current_agent_status"]["previous_agent"] = current_state["current_agent_status"].get("current_agent")
        
        # Store the previous agent for context
        previous_agent = current_state["current_agent_status"].get("current_agent")
        
        # Update current agent status
        current_state["current_agent_status"]["current_agent"] = runner.agent.name
        current_state["current_agent_status"]["last_agent_response"] = message

        # Determine next expected input based on current agent and state
        next_expected_input = None
        if runner.agent.name == "MutualFundAdvisorAgent":
            if "consent_given" not in current_state:
                next_expected_input = "consent"
            elif not current_state.get("consent_given"):
                next_expected_input = "consent"
            else:
                next_expected_input = "name"
        elif runner.agent.name == "UserProfileAgent":
            next_expected_input = "user_details"
        elif runner.agent.name == "InvestorClassifierAgent":
            next_expected_input = "risk_assessment"
        elif runner.agent.name == "GoalPlannerAgent":
            next_expected_input = "investment_goal"
        elif runner.agent.name == "FundRecommenderAgent":
            next_expected_input = "fund_selection"
        elif runner.agent.name == "SIPCalculatorAgent":
            next_expected_input = "sip_details"
        elif runner.agent.name == "InvestmentAgent":
            next_expected_input = "investment_confirmation"
        
        current_state["current_agent_status"]["next_expected_input"] = next_expected_input

        # Update session state
        runner.session_service.create_session(
            app_name=runner.app_name,
            user_id=user_id,
            session_id=session_id,
            state=current_state
        )
        
        # Log the state before processing
        logger.info(f"State before processing message: {current_state}")

        # Create content for the message
        content = types.Content(role="user", parts=[types.Part(text=message)])

        # Run the agent and process the response stream
        final_response = None
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response = event.content.parts[0].text.strip()
                    break
        
        if not final_response:
            raise ValidationError("No response received from agent")
        
        # Update session state with agent response
        current_state["current_agent_status"]["last_agent_response"] = final_response
        
        # Handle consent response
        if runner.agent.name == "MutualFundAdvisorAgent" and "consent" in next_expected_input:
            if "yes" in message.lower() or "sure" in message.lower() or "okay" in message.lower():
                current_state["consent_given"] = True
                current_state["current_agent_status"]["next_expected_input"] = "name"
            elif "no" in message.lower() or "don't" in message.lower() or "not" in message.lower():
                current_state["consent_given"] = False
                final_response = "I understand. Without your consent, I cannot proceed with collecting personal information. Please let me know if you change your mind."
        
        # Add to interaction history
        if "interaction_history" not in current_state:
            current_state["interaction_history"] = []
        current_state["interaction_history"].append({
            "agent": runner.agent.name,
            "message": final_response,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        # Update the session state
        runner.session_service.create_session(
            app_name=runner.app_name,
            user_id=user_id,
            session_id=session_id,
            state=current_state
        )
        
        # Log the state after processing
        logger.info(f"State after processing message: {current_state}")
        
        # Return user-friendly message
        return {"message": final_response}

    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return {"message": f"I need some clarification: {str(e)}"}
    except Exception as e:
        logger.error(f"Error in call_agent_async: {str(e)}")
        return {"message": f"I apologize, but I encountered an error: {str(e)}"}
