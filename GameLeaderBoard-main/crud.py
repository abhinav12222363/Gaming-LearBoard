from sqlalchemy.orm import Session
from models import GameSession, Leaderboard, User
from sqlalchemy import text
from schemas import PlayerRank
from cache import (
    cache_delete,
    cache_get,
    cache_set,
    LEADERBOARD_TOP_CACHE_KEY,
    PLAYER_RANK_CACHE_KEY_PREFIX,
    cache_delete_pattern,
)

LEADERBOARD_CACHE_TTL_SECONDS = 30
PLAYER_RANK_CACHE_TTL_SECONDS = 30


def recalculate_leaderboard_ranks(db: Session, use_dense_rank: bool = False):
    rank_func = "DENSE_RANK" if use_dense_rank else "RANK"
    db.execute(
        text(
            f"""
            WITH ranked AS (
                SELECT
                    id,
                    {rank_func}() OVER (ORDER BY total_score DESC) AS computed_rank
                FROM leaderboard
            )
            UPDATE leaderboard AS lb
            SET rank = ranked.computed_rank
            FROM ranked
            WHERE lb.id = ranked.id
            """
        )
    )


def submit_score(db: Session, user_id: int, score: int):
    """
    Atomic score submission flow:
    1) Ensure user exists.
    2) Insert raw game session for auditability.
    3) Update cumulative leaderboard score.
    4) Recalculate rank column using SQL window functions.
    5) Invalidate affected caches after commit.
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
            db.add(Leaderboard(user_id=user_id, total_score=score, rank=0))

        recalculate_leaderboard_ranks(db)

    cache_delete(f"{PLAYER_RANK_CACHE_KEY_PREFIX}{user_id}")
    cache_delete_pattern(f"{PLAYER_RANK_CACHE_KEY_PREFIX}*")
    cache_delete(LEADERBOARD_TOP_CACHE_KEY)


def get_top_leaderboard(db: Session):
    cached = cache_get(LEADERBOARD_TOP_CACHE_KEY)
    if cached is not None:
        return cached

    top_players = (
        db.query(Leaderboard.user_id, Leaderboard.total_score, Leaderboard.rank)
        .order_by(Leaderboard.rank.asc(), Leaderboard.user_id.asc())
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

    result = (
        db.query(Leaderboard.user_id, Leaderboard.total_score, Leaderboard.rank)
        .filter(Leaderboard.user_id == user_id)
        .first()
    )
    if result:
        player = PlayerRank(user_id=result.user_id, total_score=result.total_score, rank=result.rank)
        cache_set(cache_key, player.dict(), ex=PLAYER_RANK_CACHE_TTL_SECONDS)
        return player

    return PlayerRank(user_id=user_id, total_score=0, rank=-1)
