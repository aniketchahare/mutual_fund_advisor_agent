from datetime import datetime

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

# def display_state(
#     session_service, app_name, user_id, session_id, label="Current State"
# ):
#     """Display the current session state in a formatted way."""
#     try:
#         session = session_service.get_session(
#             app_name=app_name, user_id=user_id, session_id=session_id
#         )

#         # Format the output with clear sections
#         print(f"\n{'-' * 10} {label} {'-' * 10}")

#         # Handle user profile information
#         user_profile = session.state.get("user_profile", {})
#         if user_profile:
#             print(f"{Colors.BOLD}👤 User Profile:{Colors.RESET}")
#             print(f"  Name: {user_profile.get('name', 'Not provided')}")
#             print(f"  Age: {user_profile.get('age', 'Not provided')}")
#             print(f"  Monthly Income: {user_profile.get('monthly_income', 'Not provided')}")
#             print(f"  Risk Tolerance: {user_profile.get('risk_tolerance', 'Not provided')}")
#             print(f"  Investment Horizon: {user_profile.get('investment_horizon', 'Not provided')}")

#         # Handle investor type information
#         investor_type = session.state.get("investor_type", {})
#         if investor_type:
#             print(f"\n{Colors.BOLD}📊 Investor Type:{Colors.RESET}")
#             print(f"  Type: {investor_type.get('investor_type', 'Not determined')}")
#             print(f"  Investment Goal: {investor_type.get('investment_goal', 'Not set')}")

#         # Handle investment goal information
#         investment_goal = session.state.get("investment_goal", {})
#         if investment_goal:
#             print(f"\n{Colors.BOLD}🎯 Investment Goal:{Colors.RESET}")
#             print(f"  Goal Name: {investment_goal.get('goal_name', 'Not set')}")
#             print(f"  Time Horizon (Years): {investment_goal.get('time_horizon_years', 'Not specified')}")

#         # Handle fund recommendations
#         fund_recommendations = session.state.get("fund_recommendations", {})
#         if fund_recommendations:
#             print(f"\n{Colors.BOLD}💰 Fund Recommendations:{Colors.RESET}")
#             print(f"  Fund ID: {fund_recommendations.get('fund_id', 'Not selected')}")
#             print(f"  Fund Name: {fund_recommendations.get('fund_name', 'Not selected')}")
#             print(f"  Fund Type: {fund_recommendations.get('fund_type', 'Not specified')}")
#             print(f"  Fund Risk: {fund_recommendations.get('fund_risk', 'Not specified')}")
#             print(f"  Fund Return: {fund_recommendations.get('fund_return', 'Not specified')}")
#             print(f"  Fund Expense Ratio: {fund_recommendations.get('fund_expense_ratio', 'Not specified')}")

#         # Handle selected fund information
#         selected_fund = session.state.get("selected_fund", {})
#         if selected_fund:
#             print(f"\n{Colors.BOLD}✅ Selected Fund:{Colors.RESET}")
#             print(f"  Fund ID: {selected_fund.get('fund_id', 'Not selected')}")
#             print(f"  Fund Name: {selected_fund.get('fund_name', 'Not selected')}")
#             print(f"  Fund Type: {selected_fund.get('fund_type', 'Not specified')}")
#             print(f"  Fund Risk: {selected_fund.get('fund_risk', 'Not specified')}")
#             print(f"  Fund Return: {selected_fund.get('fund_return', 'Not specified')}")
#             print(f"  Fund Expense Ratio: {selected_fund.get('fund_expense_ratio', 'Not specified')}")

#         # Handle SIP calculator output
#         sip_calculator = session.state.get("sip_calculator_output", {})
#         if sip_calculator:
#             print(f"\n{Colors.BOLD}📈 SIP Calculator Output:{Colors.RESET}")
#             print(f"  SIP Amount: {sip_calculator.get('sip_amount', 'Not calculated')}")
#             print(f"  SIP Duration: {sip_calculator.get('sip_duration', 'Not specified')}")
#             print(f"  SIP Return: {sip_calculator.get('sip_return', 'Not calculated')}")

#         # Handle investment status
#         investment_status = session.state.get("investment_status", {})
#         if investment_status:
#             print(f"\n{Colors.BOLD}📊 Investment Status:{Colors.RESET}")
#             print(f"  SIP Initiated: {investment_status.get('sip_initiated', 'Not initiated')}")

#         # Handle interaction history
#         interaction_history = session.state.get("interaction_history", [])
#         if interaction_history:
#             print(f"\n{Colors.BOLD}📝 Interaction History:{Colors.RESET}")
#             for idx, interaction in enumerate(interaction_history, 1):
#                 if isinstance(interaction, dict):
#                     action = interaction.get("action", "interaction")
#                     timestamp = interaction.get("timestamp", "unknown time")
#                     if action == "user_query":
#                         query = interaction.get("query", "")
#                         print(f'  {idx}. User query at {timestamp}: "{query}"')
#                     elif action == "agent_response":
#                         agent = interaction.get("agent", "unknown")
#                         response = interaction.get("response", "")
#                         if len(response) > 100:
#                             response = response[:97] + "..."
#                         print(f'  {idx}. {agent} response at {timestamp}: "{response}"')
#                     else:
#                         details = ", ".join(
#                             f"{k}: {v}"
#                             for k, v in interaction.items()
#                             if k not in ["action", "timestamp"]
#                         )
#                         print(
#                             f"  {idx}. {action} at {timestamp}"
#                             + (f" ({details})" if details else "")
#                         )
#                 else:
#                     print(f"  {idx}. {interaction}")
#         else:
#             print(f"\n{Colors.BOLD}📝 Interaction History:{Colors.RESET} None")

#         print("-" * (22 + len(label)))
#     except Exception as e:
#         print(f"Error displaying state: {e}")


async def process_agent_response(event):
    """Process and display agent response events."""
    print(f"Event ID: {event.id}, Author: {event.author}")

    # Check for specific parts first
    has_specific_part = False
    if event.content and event.content.parts:
        for part in event.content.parts:
            if hasattr(part, "text") and part.text and not part.text.isspace():
                print(f"  Text: '{part.text.strip()}'")

    # Check for final response after specific parts
    final_response = None
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


async def call_agent_async(runner, user_id, session_id, query):
    """Call the agent asynchronously with the user's query."""
    content = types.Content(role="user", parts=[types.Part(text=query)])
    print(
        f"\n{Colors.BG_GREEN}{Colors.BLACK}{Colors.BOLD}--- Running Query: {query} ---{Colors.RESET}"
    )
    final_response_text = None
    agent_name = None
    
    # After final response and agent work is done
    try:
        # Get session state after agent run
        session = await runner.session_service.get_session(user_id, session_id)
        state = session.state

        # ✅ Check if agent flow is complete (custom condition)
        if state.get("sip_started") is True:
            print(f"{Colors.BG_BLUE}{Colors.WHITE}Session complete. Deleting session...{Colors.RESET}")
            await runner.session_service.delete_session(user_id, session_id)
        else:
            print(f"{Colors.CYAN}Session not yet complete. Keeping session active.{Colors.RESET}")

    except Exception as e:
        print(f"{Colors.BG_RED}{Colors.WHITE}Error while checking or deleting session: {e}{Colors.RESET}")


    # Display state before processing the message
    # display_state(
    #     runner.session_service,
    #     runner.app_name,
    #     user_id,
    #     session_id,
    #     "State BEFORE processing",
    # )

    try:
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=content
        ):
            # Capture the agent name from the event if available
            if event.author:
                agent_name = event.author
            print(f"Agent name: {agent_name}")
            print(f"Event: {event}")
            response = await process_agent_response(event)
            if response:
                final_response_text = response
    except ValueError as e:
        if "fromisoformat" in str(e):
            print(f"{Colors.BG_RED}{Colors.WHITE}ERROR: DateTime parsing issue. This might be due to database serialization. Trying to continue...{Colors.RESET}")
            # Try to continue with a generic error message
            final_response_text = "I encountered a technical issue with the session data. Let me help you start fresh. Please try your question again."
        else:
            print(f"{Colors.BG_RED}{Colors.WHITE}ERROR during agent run: {e}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.BG_RED}{Colors.WHITE}ERROR during agent run: {e}{Colors.RESET}")

    # Display state after processing the message
    # display_state(
    #     runner.session_service,
    #     runner.app_name,
    #     user_id,
    #     session_id,
    #     "State AFTER processing",
    # )

    print(f"{Colors.YELLOW}{'-' * 30}{Colors.RESET}")
    return final_response_text
