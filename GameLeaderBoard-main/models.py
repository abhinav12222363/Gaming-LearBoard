from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Index, CheckConstraint
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    join_date = Column(TIMESTAMP, server_default=func.now())

class GameSession(Base):
    __tablename__ = "game_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Integer, nullable=False)
    game_mode = Column(String(50), nullable=False, default="solo")
    timestamp = Column(TIMESTAMP, server_default=func.now(), index=True)

    __table_args__ = (
        CheckConstraint("score >= 0", name="ck_game_sessions_score_non_negative"),
    )


class Leaderboard(Base):
    __tablename__ = "leaderboard"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    total_score = Column(Integer, nullable=False, default=0)
    rank = Column(Integer, index=True)

    __table_args__ = (
        CheckConstraint("total_score >= 0", name="ck_leaderboard_total_score_non_negative"),
        Index("ix_leaderboard_total_score_desc_user_id", total_score.desc(), user_id.asc()),
    )
