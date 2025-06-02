from fastapi import FastAPI, HTTPException
from typing import Dict, Any
from pydantic import BaseModel
import uvicorn
import json

# Simulated data store (would typically connect to Atheris agents)
database = {
    "sentiment_scores": {},
    "contributors": {},
    "alerts": []
}

app = FastAPI(title="Atheris API Backend", version="1.0")

class SentimentRequest(BaseModel):
    message_id: str
    content: str

class ContributorRequest(BaseModel):
    wallet: str
    name: str

class AlertRequest(BaseModel):
    type: str
    message: str


@app.get("/")
def root():
    return {"message": "Atheris API Backend is running."}


@app.post("/sentiment/analyze")
def analyze_sentiment(req: SentimentRequest):
    score = len([w for w in req.content.lower().split() if w in ["good", "great", "bad", "broken"]])
    database["sentiment_scores"][req.message_id] = score
    return {"message_id": req.message_id, "sentiment_score": score}


@app.get("/sentiment/{message_id}")
def get_sentiment(message_id: str):
    if message_id not in database["sentiment_scores"]:
        raise HTTPException(status_code=404, detail="Message not found.")
    return {"message_id": message_id, "score": database["sentiment_scores"][message_id]}


@app.post("/contributors/register")
def register_contributor(req: ContributorRequest):
    database["contributors"][req.wallet] = {"name": req.name, "tasks": 0}
    return {"wallet": req.wallet, "name": req.name}


@app.get("/contributors")
def list_contributors():
    return database["contributors"]


@app.post("/alerts")
def create_alert(req: AlertRequest):
    alert = {"type": req.type, "message": req.message}
    database["alerts"].append(alert)
    return {"status": "ok", "alert": alert}


@app.get("/alerts")
def list_alerts():
    return database["alerts"]


@app.get("/status")
def status():
    return {
        "sentiments": len(database["sentiment_scores"]),
        "contributors": len(database["contributors"]),
        "alerts": len(database["alerts"])
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
