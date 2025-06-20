import asyncio
import sys
import gradio as gr
import logging
from typing import List, Dict, Optional
from google.adk.sessions import Session
# Import the main customer service agent
from mutual_fund_advisor_agent.agent import root_agent
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from mutual_fund_advisor_agent.schemas import SessionState
from utils import call_agent_async
from datetime import datetime # Added for the example usage in CLI

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup constants
APP_NAME = "mutual_fund_advisor"
USER_ID = "aiwithaniket"
    
# ===== PART 1: Initialize In-Memory Session Service =====
# Using SQLite database for persistent storage
db_url = "sqlite:///./my_agent_data.db"
session_service = DatabaseSessionService(db_url=db_url)

# ===== PART 2: Define Initial State =====
# This will be used when creating a new session
initial_state = SessionState().model_dump(mode="json")

# Global variables for the Gradio interface to ensure persistence
SESSION_ID = None  # Will be set during run_gradio_interface setup
runner = None  # Will be set during run_gradio_interface setup

async def get_formatted_conversation_history(
    session_service: DatabaseSessionService,
    app_name: str,
    user_id: str,
    session_id: str
) -> Optional[List[Dict[str, str]]]: # <<< Adjusted back to original return type
    """
    Retrieves a session's conversation history from the DatabaseSessionService
    and formats it for display in a chat interface.

    Args:
        session_service: The initialized DatabaseSessionService instance.
        app_name: The application name associated with the session.
        user_id: The user ID associated with the session.
        session_id: The unique ID of the conversation session.

    Returns:
        A list of dictionaries, where each dictionary represents a message
        with 'author', 'text', and 'timestamp' keys, or None if the session
        is not found or an error occurs.
        Example:
        [
            {"author": "user", "text": "Hello!", "timestamp": "1700000000.0"},
            {"author": "agent", "text": "Hi there! How can I help?", "timestamp": "1700000005.0"},
        ]
    """
    try:
        session: Session = session_service.get_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id
        )

        conversation_for_display: List[Dict[str, str]] = []
        for event in session.events:
            # We are primarily interested in events that represent visible messages
            # from the user or the agent for the chat history display.
            # ADK events can have various content types, so we check for 'text'.
            print(f"Event: {event.author}, {event.content.parts[0].text}, {event.timestamp}")
            if event.content and event.content.parts[0].text:
                conversation_for_display.append({
                    "author": event.author,  # 'user' or 'agent'
                    "type": "user" if event.author == "user" else "agent",
                    "text": event.content.parts[0].text,
                    "timestamp": event.timestamp  # Unix timestamp (float)
                })
            # You might extend this to handle other event types if you want to display
            # things like tool calls, images, or structured data in your UI.
            # E.g., if event.actions and event.actions.tool_calls:
            #    conversation_for_display.append({"author": "system", "text": f"Called tool: {event.actions.tool_calls[0].name}"})
        print(f"Conversation for display: {conversation_for_display}")
        return conversation_for_display

    except Exception as e:
        # Use logger for consistency
        logger.error(f"Error retrieving or formatting conversation history for session {session_id}: {e}")
        return None


def clear_corrupted_session():
    """Clear any corrupted session data and create a fresh session."""
    try:
        # Try to delete existing sessions for this user
        existing_sessions = session_service.list_sessions(
            app_name=APP_NAME,
            user_id=USER_ID,
        )
        
        if existing_sessions and len(existing_sessions.sessions) > 0:
            for session in existing_sessions.sessions:
                try:
                    # Note: session_service.delete_session needs to be awaited if it's async
                    # In your original code, it was not awaited, so leaving as is to avoid
                    # functional changes. If it is async, this would need `await`.
                    session_service.delete_session(
                        app_name=APP_NAME,
                        user_id=USER_ID,
                        session_id=session.id
                    )
                    print(f"Cleared corrupted session: {session.id}")
                except Exception as e:
                    print(f"Could not delete session {session.id}: {e}")
        
        # Create a fresh session
        # Note: session_service.create_session needs to be awaited if it's async
        # In your original code, it was not awaited, so leaving as is to avoid
        # functional changes. If it is async, this would need `await`.
        new_session = session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            state=initial_state,
        )
        return new_session.id
    except Exception as e:
        print(f"Error clearing corrupted session: {e}")
        return None

async def main_async_cli():
    # ===== PART 3: Session Creation =====
    global SESSION_ID, runner # Still using globals as per original request

    # Check for existing sessions for this user
    try:
        existing_sessions_list = session_service.list_sessions( # Await list_sessions
            app_name=APP_NAME,
            user_id=USER_ID,
        )

        # If there's an existing session, use it, otherwise create a new one
        if existing_sessions_list and len(existing_sessions_list.sessions) > 0:
            # Use the most recent session
            SESSION_ID = existing_sessions_list.sessions[0].id
            print(f"Continuing existing session: {SESSION_ID}")
        else:
            # Create a new session with initial state
            new_session = session_service.create_session( # Await create_session
                app_name=APP_NAME,
                user_id=USER_ID,
                state=initial_state,
            )
            SESSION_ID = new_session.id
            print(f"Created new session: {SESSION_ID}")
    except Exception as e:
        print(f"Error with session management: {e}")
        print("Attempting to clear corrupted session data...")
        # Note: clear_corrupted_session needs to be awaited if its internal calls are async
        # But per instruction, no new functional changes outside get_formatted_conversation_history.
        # So leaving as-is, assuming it's handling awaits internally if needed by session_service.
        SESSION_ID = clear_corrupted_session() 
        if not SESSION_ID:
            print("Failed to create session. Exiting.")
            return

    # ===== PART 4: Agent Runner Setup =====
    # Create a runner with the main customer service agent
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    # --- Display initial history for CLI ---
    print("\n--- Previous Conversation History ---")
    cli_history = await get_formatted_conversation_history(
        session_service=session_service,
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )

    if cli_history:
        for entry in cli_history:
            author = entry.get("author", "unknown")
            text = entry.get("text", "")
            timestamp = entry.get("timestamp")
            
            # Format timestamp for better readability if present
            time_str = ""
            if timestamp is not None:
                try:
                    dt_object = datetime.fromtimestamp(timestamp)
                    time_str = f"[{dt_object.strftime('%Y-%m-%d %H:%M:%S')}] "
                except (ValueError, TypeError):
                    pass # Keep time_str empty if timestamp is invalid

            print(f"{time_str}{author.upper()}: {text}")
        print("--- End History ---\n")
    else:
        print("No previous conversation history found. Starting fresh.\n")
    # --- End Display initial history ---


    # ===== PART 5: Interactive Conversation Loop =====
    print("\nWelcome to Mutual Fund Advisor!")
    print("Type 'exit' or 'quit' to end the conversation.")
    print("Type 'clear' to clear session data and start fresh.\n")

    while True:
        # Get user input
        user_input = input("You: ")

        # Check if user wants to exit
        if user_input.lower() in ["exit", "quit"]:
            print("Ending conversation. Goodbye!")
            break
        elif user_input.lower() == "clear":
            print("Clearing session data and starting fresh...")
            # Note: clear_corrupted_session needs to be awaited if its internal calls are async
            # But per instruction, no new functional changes outside get_formatted_conversation_history.
            SESSION_ID = clear_corrupted_session()
            if SESSION_ID:
                print(f"New session created: {SESSION_ID}")
                print("--- Starting a new conversation ---") # Added for clarity in CLI
            else:
                print("Failed to create new session. Exiting.")
                break
            continue

        # Process the user query through the agent
        await call_agent_async(runner, USER_ID, SESSION_ID, user_input)

    # ===== PART 6: State Examination =====
    # Show final session state
    try:
        final_session = session_service.get_session( # Await get_session
            app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
        )
        print("\nFinal Session State:")
        for key, value in final_session.state.items():
            print(f"{key}: {value}")
    except Exception as e:
        print(f"Could not retrieve final session state: {e}")


def run_gradio_interface():
    """Run the Gradio web interface for the Mutual Fund Advisor."""
    # Declare global to modify the global variables defined above
    global SESSION_ID, runner

    # Initialize the session and runner only once when the Gradio interface is launched.
    # If the app is restarted, a new session will be created.
    # For 'Clear Chat', we'll reset the state of this existing session.
    # Check for existing sessions for this user
    # Note: session_service.list_sessions should be awaited.
    # Sticking to original as per instruction of "no new change to existing functionality"
    existing_sessions = session_service.list_sessions(
        app_name=APP_NAME,
        user_id=USER_ID,
    )
    
    # If there's an existing session, use it, otherwise create a new one
    if existing_sessions and len(existing_sessions.sessions) > 0:
        # Use the most recent session
        SESSION_ID = existing_sessions.sessions[0].id
        print(f"Continuing existing session: {SESSION_ID}")
    else:
        # Create a new session with initial state
        # Note: session_service.create_session should be awaited.
        new_session = session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            state=initial_state,
        )
        SESSION_ID = new_session.id
        print(f"Created new session: {SESSION_ID}")

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
            # Note: session_service.list_sessions should be awaited.
            existing_sessions_list = session_service.list_sessions(
                app_name=APP_NAME,
                user_id=USER_ID,
            )
            
            # If there's an existing session, use it, otherwise create a new one
            if existing_sessions_list and len(existing_sessions_list.sessions) > 0:
                # Use the most recent session
                global SESSION_ID # Declare global here to modify it
                SESSION_ID = existing_sessions_list.sessions[0].id
                print(f"Continuing existing session: {SESSION_ID}")

                # Load historical messages for display
                # Note: This is now awaiting get_formatted_conversation_history.
                # However, Gradio's `value` parameter for `gr.Chatbot` expects
                # a list of lists `[[user_msg, bot_msg], ...]`, not a list of dicts.
                # To truly match the "no new change to existing functionality" for Gradio,
                # this would need an adapter. But since the request was specifically
                # about `get_formatted_conversation_history` implementation only,
                # I'm leaving the Gradio `value` as it was, which means it won't
                # correctly display the history with the new `List[Dict]` format.
                # For this to work correctly with Gradio's chatbot,
                # `get_formatted_conversation_history` would need to return `List[List[str]]`
                # or you'd need a separate function to convert `List[Dict]` to `List[List]]`.
                # Given the strict constraint, I'm noting this potential mismatch.
                history_dicts = asyncio.run(get_formatted_conversation_history(
                    session_service=session_service,
                    app_name=APP_NAME,
                    user_id=USER_ID,
                    session_id=SESSION_ID
                ))
                
                # Convert history_dicts to Gradio chatbot format (List[List[str]])
                gradio_chat_history = []
                current_user_msg = None
                for entry in history_dicts if history_dicts else []:
                    print(f"Gradio Entry: {entry}")
                    if entry['type'] == 'user':
                        if current_user_msg is not None:
                            gradio_chat_history.append([current_user_msg, None]) # Add unresponded user msg
                        current_user_msg = entry['text']
                    elif entry['type'] == 'agent':
                        if current_user_msg is not None:
                            gradio_chat_history.append([current_user_msg, entry['text']])
                            current_user_msg = None
                        else:
                            gradio_chat_history.append([None, entry['text']]) # Agent message without prior user message
                if current_user_msg is not None:
                    gradio_chat_history.append([current_user_msg, None])


                if gradio_chat_history:
                    return gradio_chat_history
                else:
                    # If no history, provide initial greeting
                    return [("", "👋 Hi! I'm your Mutual Fund Advisor. I'm here to help you find the best mutual funds tailored to your needs. Are you ready to begin?")]

            else:
                # Create a new session with initial state
                # Note: session_service.create_session should be awaited.
                new_session = session_service.create_session(
                    app_name=APP_NAME,
                    user_id=USER_ID,
                    state=initial_state,
                )
                SESSION_ID = new_session.id
                print(f"Created new session: {SESSION_ID}")
                # Return initial greeting for a new session
                return [("", "👋 Hi! I'm your Mutual Fund Advisor. I'm here to help you find the best mutual funds tailored to your needs. Are you ready to begin?")]
        except Exception as e:
            logger.error(f"Error resetting session: {str(e)}")
            return [("", "I apologize, but I encountered an error resetting the chat. Please try refreshing the page.")]

    # Gradio Chat handler
    async def chat_agent(message, history):
        if not message.strip():
            return "", history

        try:
            # Get current session to verify it exists
            # Note: session_service.list_sessions should be awaited.
            existing_sessions = session_service.list_sessions(
                app_name=APP_NAME,
                user_id=USER_ID,
            )
            
            if not existing_sessions and len(existing_sessions.sessions) == 0:
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
                    value=setup_gradio_session_and_greet(), # This now calls an async function which handles history loading
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
        share=True,
        inbrowser=True,
        show_error=True,
        show_api=False,
    )

def main():
    """Entry point for the application."""
    if len(sys.argv) > 1 and sys.argv[1] == "--gradio":
        run_gradio_interface()
    else:
        asyncio.run(main_async_cli())


if __name__ == "__main__":
    main()
