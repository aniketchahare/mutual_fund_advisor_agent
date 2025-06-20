from fastapi import FastAPI, HTTPException
from typing import Dict
from google.adk.sessions import DatabaseSessionService
from mutual_fund_advisor_agent.agent import root_agent
from mutual_fund_advisor_agent.schemas import SessionState
from google.adk.runners import Runner
from utils import call_agent_async

# FastAPI app
app = FastAPI()

# Constants
APP_NAME = "mutual_fund_advisor"
DB_URL = "sqlite:///./mutual_fund_advisor.db"
session_service = DatabaseSessionService(db_url=DB_URL)
initial_state = SessionState().model_dump(mode="json")

# Runner (reused across requests)
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
user_sessions: Dict[str, str] = {}  # simple cache (use Redis or DB for prod)

# -------------------------------
# 1. Start or Get Existing Session
# -------------------------------
@app.get("/start/{user_id}")
async def start_session(user_id: str):
    sessions = session_service.list_sessions(app_name=APP_NAME, user_id=user_id)
    if sessions.sessions:
        session_id = sessions.sessions[0].id
    else:
        session = session_service.create_session(app_name=APP_NAME, user_id=user_id, state=initial_state)
        session_id = session.id

    user_sessions[user_id] = session_id
    return {"session_id": session_id}

# -------------------------------
# 2. Send a message to the agent
# -------------------------------
@app.post("/message/{user_id}/{session_id}/{message}")
async def send_message(user_id: str, session_id: str, message: str):
    try:
        response = await call_agent_async(runner, user_id, session_id, message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------------
# 3. Get Conversation History
# -------------------------------
@app.get("/history/{user_id}/{session_id}")
async def get_history(user_id: str, session_id: str):
    try:
        session = session_service.get_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)
        messages = [
            {
                "author": e.author,
                "text": e.content.parts[0].text if e.content and e.content.parts else "",
                "timestamp": e.timestamp,
            }
            for e in session.events
            if e.content and e.content.parts
        ]
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Session not found")
