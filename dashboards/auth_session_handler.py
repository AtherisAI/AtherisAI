from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict
import uuid
import time

class SessionManager:
    def __init__(self, timeout_minutes: int = 30):
        self.sessions: Dict[str, Dict] = {}
        self.timeout = timeout_minutes * 60
        print(f"[SessionManager] Initialized with timeout: {self.timeout} seconds")

    def create_session(self, user_id: str) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "user_id": user_id,
            "created_at": time.time(),
            "last_active": time.time()
        }
        print(f"[SessionManager] Created session for user: {user_id}")
        return session_id

    def validate_session(self, session_id: str) -> bool:
        session = self.sessions.get(session_id)
        if not session:
            print("[SessionManager] Session ID not found.")
            return False
        if time.time() - session["last_active"] > self.timeout:
            print("[SessionManager] Session expired.")
            del self.sessions[session_id]
            return False
        session["last_active"] = time.time()
        return True

    def get_user(self, session_id: str) -> str:
        session = self.sessions.get(session_id)
        if session:
            return session["user_id"]
        raise HTTPException(status_code=401, detail="Invalid or expired session.")

    def destroy_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]
            print(f"[SessionManager] Destroyed session: {session_id}")


# FastAPI example integration
from fastapi import FastAPI, Cookie
app = FastAPI()
session_mgr = SessionManager()

@app.post("/login")
def login(user_id: str, response: Response):
    session_id = session_mgr.create_session(user_id)
    response.set_cookie(key="session_id", value=session_id, httponly=True)
    return {"message": "Login successful", "session_id": session_id}

@app.get("/secure-data")
def secure_data(session_id: str = Cookie(None)):
    if not session_mgr.validate_session(session_id):
        raise HTTPException(status_code=401, detail="Session invalid or expired.")
    user = session_mgr.get_user(session_id)
    return {"user": user, "data": "This is secure Atheris data."}

@app.post("/logout")
def logout(session_id: str = Cookie(None), response: Response = None):
    session_mgr.destroy_session(session_id)
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie("session_id")
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8090)
