from pydantic import BaseModel
from typing import Optional

class ScoreSubmission(BaseModel):
    user_id: int
    score: int

class LeaderboardEntry(BaseModel):
    user_id: int
    total_score: int
    rank: Optional[int]

class PlayerRank(BaseModel):
    user_id: int
    total_score: int
    rank: Optional[int]
