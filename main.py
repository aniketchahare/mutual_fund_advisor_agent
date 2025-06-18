import asyncio
import sys
import gradio as gr
import logging

# Import the main customer service agent
from mutual_fund_advisor_agent.agent import root_agent
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from utils import call_agent_async

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup constants
APP_NAME = "Mutual Fund Advisor"
USER_ID = "aiwithaniket"
    
# ===== PART 1: Initialize In-Memory Session Service =====
# Using in-memory storage for this example (non-persistent)
session_service = InMemorySessionService()

# Global variables for the Gradio interface to ensure persistence
SESSION_ID = None  # Will be set during run_gradio_interface setup
runner = None  # Will be set during run_gradio_interface setup

# ===== PART 2: Define Initial State =====
# This will be used when creating a new session
initial_state = {}


async def main_async_cli():
    # ===== PART 3: Session Creation =====
    # Create a new session with initial state
    new_session = session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        state=initial_state,
    )
    SESSION_ID = new_session.id
    print(f"Created new session: {SESSION_ID}")

    # ===== PART 4: Agent Runner Setup =====
    # Create a runner with the main customer service agent
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    # ===== PART 5: Interactive Conversation Loop =====
    print("\nWelcome to Mutual Fund Advisor!")
    print("Type 'exit' or 'quit' to end the conversation.\n")

    while True:
        # Get user input
        user_input = input("You: ")

        # Check if user wants to exit
        if user_input.lower() in ["exit", "quit"]:
            print("Ending conversation. Goodbye!")
            break

        # Update interaction history with the user's query
        # add_user_query_to_history(
        #     session_service, APP_NAME, USER_ID, SESSION_ID, user_input
        # )

        # Process the user query through the agent
        await call_agent_async(runner, USER_ID, SESSION_ID, user_input)

    # ===== PART 6: State Examination =====
    # Show final session state
    final_session = session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    print("\nFinal Session State:")
    for key, value in final_session.state.items():
        print(f"{key}: {value}")


def run_gradio_interface():
    """Run the Gradio web interface for the Mutual Fund Advisor."""
    # Declare global to modify the global variables defined above
    global SESSION_ID, runner

    # Initialize the session and runner only once when the Gradio interface is launched.
    # If the app is restarted, a new session will be created.
    # For 'Clear Chat', we'll reset the state of this existing session.
    new_session = session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        state=initial_state.copy(),
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
            
            # Reset the session state to initial state
            session_service.create_session(
                app_name=APP_NAME,
                user_id=USER_ID,
                session_id=SESSION_ID,
                state=initial_state.copy()
            )
            
            # Return initial greeting
            return [("", "👋 Hi! I'm your Mutual Fund Advisor. I'm here to help you find the best mutual funds tailored to your needs. To start, I'll need to gather some basic details. Are you ready to begin?")]
        except Exception as e:
            logger.error(f"Error resetting session: {str(e)}")
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

            # Process the user query through the agent
            agent_response = await call_agent_async(
                runner=runner,
                user_id=USER_ID,
                session_id=SESSION_ID,
                query=message
            )

            # Add agent response to history in Gradio chatbot
            if agent_response:
                # call_agent_async returns a string, so we use it directly
                history.append((message, agent_response))
            else:
                # Handle case where no response was received
                history.append((message, "I apologize, but I didn't receive a response. Please try again."))

            return "", history

        except Exception as e:
            logger.error(f"Error in chat_agent: {str(e)}")
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
            [chatbot],
            api_name="clear"
        )

    # Launch Gradio with improved configuration
    ui.launch(
        share=False,
        inbrowser=True,
        show_error=True,
        show_api=False
    )

def main():
    """Entry point for the application."""
    if len(sys.argv) > 1 and sys.argv[1] == "--gradio":
        run_gradio_interface()
    else:
        asyncio.run(main_async_cli())


if __name__ == "__main__":
    main()
