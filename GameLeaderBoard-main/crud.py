from sqlalchemy.orm import Session
from models import GameSession, Leaderboard, User
from sqlalchemy import func
from schemas import PlayerRank
from cache import (
    cache_delete,
    cache_get,
    cache_set,
    LEADERBOARD_TOP_CACHE_KEY,
    PLAYER_RANK_CACHE_KEY_PREFIX,
)

LEADERBOARD_CACHE_TTL_SECONDS = 30
PLAYER_RANK_CACHE_TTL_SECONDS = 30


def submit_score(db: Session, user_id: int, score: int):
    """
    Atomic score submission flow:
    1) Ensure user exists.
    2) Insert raw game session for auditability.
    3) Update cumulative leaderboard score.
    4) Invalidate affected caches after commit.
    """
    with db.begin():
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            db.add(User(id=user_id, username=f"user_{user_id}"))

        db.add(GameSession(user_id=user_id, score=score, game_mode="solo"))

        leaderboard = db.query(Leaderboard).filter_by(user_id=user_id).with_for_update().first()
        if leaderboard:
            leaderboard.total_score += score
        else:
            db.add(Leaderboard(user_id=user_id, total_score=score))

    # Cache invalidation happens after successful commit.
    cache_delete(f"{PLAYER_RANK_CACHE_KEY_PREFIX}{user_id}")
    cache_delete(LEADERBOARD_TOP_CACHE_KEY)


def get_top_leaderboard(db: Session):
    cached = cache_get(LEADERBOARD_TOP_CACHE_KEY)
    if cached is not None:
        return cached

    ranked_subquery = db.query(
        Leaderboard.user_id,
        Leaderboard.total_score,
        func.rank().over(order_by=Leaderboard.total_score.desc()).label("rank"),
    ).subquery()

    top_players = (
        db.query(ranked_subquery)
        .order_by(ranked_subquery.c.total_score.desc())
        .limit(10)
        .all()
    )

    result = [
        {
            "user_id": p.user_id,
            "total_score": p.total_score,
            "rank": p.rank,
        }
        for p in top_players
    ]
    cache_set(LEADERBOARD_TOP_CACHE_KEY, result, ex=LEADERBOARD_CACHE_TTL_SECONDS)
    return result


def get_player_rank(db: Session, user_id: int):
    cache_key = f"{PLAYER_RANK_CACHE_KEY_PREFIX}{user_id}"
    cached = cache_get(cache_key)
    if cached is not None:
        return PlayerRank(**cached)

    subquery = db.query(
        Leaderboard.user_id,
        Leaderboard.total_score,
        func.rank().over(order_by=Leaderboard.total_score.desc()).label("rank"),
    ).subquery()

    result = db.query(subquery).filter(subquery.c.user_id == user_id).first()
    if result:
        player = PlayerRank(user_id=result.user_id, total_score=result.total_score, rank=result.rank)
        cache_set(cache_key, player.dict(), ex=PLAYER_RANK_CACHE_TTL_SECONDS)
        return player

    return PlayerRank(user_id=user_id, total_score=0, rank=-1)
