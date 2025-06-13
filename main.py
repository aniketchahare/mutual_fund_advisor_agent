import asyncio
import sys
import gradio as gr
from mutual_fund_advisor_agent.agent import root_agent
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from utils import Colors, add_user_query_to_history, call_agent_async, display_state, add_agent_response_to_history

load_dotenv()

# ===== PART 1: Initialize In-Memory Session Service =====
# Using in-memory storage for this example (non-persistent)
# This should be global so it's initialized only once for the application.
session_service = InMemorySessionService()

# Global variables for the Gradio interface to ensure persistence
APP_NAME = "Mutual Fund Advisor"
USER_ID = "aiwithaniket" # In a real app, this would be dynamic per user.
SESSION_ID = None # Will be set during run_gradio_interface setup
runner = None # Will be set during run_gradio_interface setup

# ===== PART 2: Define Initial State Template =====
# This template will be used to create a fresh state for each new session or session reset.
initial_state_template = {
    "user_profile": {
        "name": "",
        "age": "",
        "gender": "",
        "monthly_income": "",
        "investment_experience": "",
    },
    "investor_classification": {
        "type": "",
        "risk_tolerance_score": None
    },
    "investment_goal": {
        "goal_type": "",
        "target_amount": None,
        "time_horizon_years": None,
        "monthly_sip_target": None
    },
    "fund_recommendations": [],
    "selected_fund": {
        "fund_id": None,
        "name": None
    },
    "investment_status": {
        "user_account_created": False,
        "logged_in_investment_portal": False,
        "sip_initiated": False,
        "sip_transaction_id": None
    },
    "current_agent_status": {
        "current_agent": None,
        "next_expected_input": None,
        "last_agent_response": None
    },
    "interaction_history": [],
}

def run_gradio_interface():
    # Declare global to modify the global variables defined above
    global SESSION_ID, runner

    # Initialize the session and runner only once when the Gradio interface is launched.
    # If the app is restarted, a new session will be created.
    # For 'Clear Chat', we'll reset the state of this existing session.
    new_session = session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        state=initial_state_template.copy(),
    )
    SESSION_ID = new_session.id
    print(f"Gradio: Created/Initialized Session ID: {SESSION_ID}")

    # Create the runner with the main customer service agent
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    def setup_gradio_session_and_greet():
        """
        Resets the current session's state and provides an initial greeting.
        Called on app load and when 'Clear Chat' is clicked.
        """
        try:
            # Get current session state
            current_session = session_service.get_session(
                app_name=APP_NAME,
                user_id=USER_ID,
                session_id=SESSION_ID
            )
            
            if not current_session:
                raise Exception(f"Session not found: {SESSION_ID}")
            
            # Get current state
            current_state = current_session.state.copy()
            
            # Initialize current agent status
            current_state["current_agent_status"] = {
                "current_agent": "MutualFundAdvisor",
                "next_expected_input": "name",
                "last_agent_response": None
            }
            
            # Update the session with new state
            session_service.create_session(
                app_name=APP_NAME,
                user_id=USER_ID,
                session_id=SESSION_ID,
                state=current_state
            )
            
            initial_greeting = "👋 Hello! I'm your Mutual Fund Advisor. Let's get started with your investment journey. What's your name?"
            add_agent_response_to_history(session_service, APP_NAME, USER_ID, SESSION_ID, "MutualFundAdvisor", initial_greeting)
            return [("", initial_greeting)]
        except Exception as e:
            print(f"{Colors.RED}Error resetting session: {e}{Colors.RESET}")
            return [("", "I apologize, but I encountered an error resetting the chat. Please try refreshing the page.")]

    # Gradio Chat handler
    async def chat_agent(message, history):
        if not message.strip():
            return "", history

        try:
            # Get current session to verify it exists
            current_session = session_service.get_session(
                app_name=APP_NAME,
                user_id=USER_ID,
                session_id=SESSION_ID
            )
            
            if not current_session:
                raise Exception(f"Session not found: {SESSION_ID}")
            
            # Get current state
            current_state = current_session.state.copy()
            
            # Add user message to history in ADK session
            add_user_query_to_history(session_service, APP_NAME, USER_ID, SESSION_ID, message)

            # Process the user query through the agent
            agent_response_text = await call_agent_async(runner, USER_ID, SESSION_ID, message)

            # Add agent response to history in Gradio chatbot
            if agent_response_text:
                # Ensure we're not displaying raw JSON if the agent accidentally returns it
                if isinstance(agent_response_text, (dict, list)):
                    agent_response_text = str(agent_response_text)
                history.append((message, agent_response_text))

            # Display current ADK session state for debugging (optional in production)
            display_state(session_service, APP_NAME, USER_ID, SESSION_ID, "Gradio Session State")

            return "", history

        except Exception as e:
            print(f"{Colors.RED}Error in chat_agent: {e}{Colors.RESET}")
            error_message = "I apologize, but I encountered an error. Please try again or refresh the page to start a new conversation."
            history.append((message, error_message))
            return "", history

    # UI Setup using gr.Chatbot
    with gr.Blocks(theme=gr.themes.Soft()) as ui:
        with gr.Row():
            gr.Markdown(
                """
                ## 🧠 Mutual Fund Advisor Chatbot
                Your personal AI assistant for mutual fund investments
                """
            )

        with gr.Row():
            with gr.Column(scale=4):
                chatbot = gr.Chatbot(
                    label="Chat History",
                    height=500,
                    show_label=True,
                    container=True,
                    bubble_full_width=False,
                    # Call the setup function to initialize session and get initial greeting
                    value=setup_gradio_session_and_greet(),
                    elem_id="chatbot"
                )

                with gr.Row():
                    message = gr.Textbox(
                        label="Type your message",
                        placeholder="Type your message here...",
                        scale=8,
                        container=False,
                        elem_id="message_input"
                    )
                    submit = gr.Button(
                        "Send",
                        variant="primary",
                        scale=1,
                        elem_id="submit_button"
                    )
                    clear = gr.Button(
                        "Clear Chat",
                        variant="secondary",
                        scale=1,
                        elem_id="clear_button"
                    )

        # Event handlers
        submit.click(
            chat_agent,
            [message, chatbot],
            [message, chatbot],
            api_name="chat"
        )

        message.submit(
            chat_agent,
            [message, chatbot],
            [message, chatbot],
            api_name="chat_enter"
        )

        clear.click(
            # On clear, re-setup the session for a fresh start by resetting the state
            setup_gradio_session_and_greet,
            None,
            [message, chatbot],
            api_name="clear"
        )

    # Launch Gradio with improved configuration
    ui.launch(
        share=False,
        inbrowser=True,
        show_error=True,
        show_api=False
    )

async def main_async_cli():
    """
    Asynchronous function for the command-line interface (CLI) mode.
    Handles interactive conversation in the terminal.
    """
    _app_name_cli = APP_NAME # Use global APP_NAME
    _user_id_cli = USER_ID   # Use global USER_ID

    # Create a new session with initial state for the CLI user
    _new_session_cli = session_service.create_session(
        app_name=_app_name_cli,
        user_id=_user_id_cli,
        state=initial_state_template.copy(),
    )
    _session_id_cli = _new_session_cli.id
    print(f"CLI: Created new session: {_session_id_cli}")

    # Create a runner for the CLI
    _runner_cli = Runner(
        agent=root_agent,
        app_name=_app_name_cli,
        session_service=session_service,
    )

    print("\nWelcome to Mutual Fund Advisor (CLI Mode)!")
    print("Type 'exit' or 'quit' to end the conversation.\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Ending conversation. Goodbye!")
            break

        add_user_query_to_history(
            session_service, _app_name_cli, _user_id_cli, _session_id_cli, user_input
        )

        await call_agent_async(_runner_cli, _user_id_cli, _session_id_cli, user_input)

    # Show final session state at the end of the CLI conversation
    display_state(session_service, _app_name_cli, _user_id_cli, _session_id_cli, "Final State (CLI)")

def main():
    """Entry point for the application."""
    if len(sys.argv) > 1 and sys.argv[1] == "--gradio":
        run_gradio_interface()
    else:
        asyncio.run(main_async_cli())


if __name__ == "__main__":
    main()
