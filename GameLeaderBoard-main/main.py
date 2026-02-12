from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, SessionLocal
from schemas import ScoreSubmission, PlayerRank, LeaderboardEntry
import crud
import logging
import newrelic.agent
import os

app = FastAPI()

# Initialize New Relic
if os.getenv("ENV") != "test" and os.getenv("NEW_RELIC_CONFIG_FILE"):
    newrelic.agent.initialize(os.getenv("NEW_RELIC_CONFIG_FILE"))
    app = newrelic.agent.asgi_application()(app)

# Enable CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("server.log"),   # Logs to file
        logging.StreamHandler()              # Logs to terminal
    ]
)

logger = logging.getLogger(__name__)


# Create tables
Base.metadata.create_all(bind=engine)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Completed with status code: {response.status_code}")
    return response

@app.post("/api/leaderboard/submit")
def submit_score(data: ScoreSubmission):
    db = SessionLocal()
    try:
        crud.submit_score(db, data.user_id, data.score)
        return {"message": "Score submitted successfully"}
    finally:
        db.close()

@app.get("/api/leaderboard/top", response_model=list[LeaderboardEntry])
def get_leaderboard():
    db = SessionLocal()
    try:
        return crud.get_top_leaderboard(db)
    finally:
        db.close()

@app.get("/api/leaderboard/rank/{user_id}", response_model=PlayerRank)
def get_player_rank(user_id: int):
    db = SessionLocal()
    try:
        return crud.get_player_rank(db, user_id)
    finally:
        db.close()
