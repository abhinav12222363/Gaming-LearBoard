from sqlalchemy.orm import Session
from models import GameSession, Leaderboard, User
from sqlalchemy import text
from fastapi import HTTPException
from schemas import PlayerRank
from cache import (
    cache_delete,
    cache_get,
    cache_set,
    LEADERBOARD_TOP_CACHE_KEY,
    PLAYER_RANK_CACHE_KEY_PREFIX,
    bump_rank_cache_version,
    get_rank_cache_version,
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
                    {rank_func}() OVER (ORDER BY total_score DESC, user_id ASC) AS computed_rank
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
    4) Shift only impacted ranks (avoid full leaderboard recomputation per write).
    5) Invalidate top and user-rank caches after commit.
    """
    if score < 0:
        raise HTTPException(status_code=400, detail="Score must be non-negative")

    with db.begin():
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            db.add(User(id=user_id, username=f"user_{user_id}"))

        db.add(GameSession(user_id=user_id, score=score, game_mode="solo"))

        leaderboard = (
            db.query(Leaderboard)
            .filter_by(user_id=user_id)
            .with_for_update()
            .first()
        )

        old_total_score = leaderboard.total_score if leaderboard else 0
        new_total_score = old_total_score + score

        if leaderboard:
            leaderboard.total_score = new_total_score
        else:
            leaderboard = Leaderboard(user_id=user_id, total_score=new_total_score, rank=1)
            db.add(leaderboard)
            db.flush()

        new_rank = db.execute(
            text(
                """
                SELECT COALESCE(COUNT(*), 0) + 1
                FROM leaderboard
                WHERE total_score > :new_total_score
                """
            ),
            {"new_total_score": new_total_score},
        ).scalar_one()

        if old_total_score == 0 and leaderboard.rank == 1:
            old_rank = db.execute(
                text("SELECT COALESCE(MAX(rank), 0) + 1 FROM leaderboard WHERE user_id != :user_id"),
                {"user_id": user_id},
            ).scalar_one()
        else:
            old_rank = leaderboard.rank if leaderboard.rank else (
                db.execute(
                    text(
                        """
                        SELECT COALESCE(COUNT(*), 0) + 1
                        FROM leaderboard
                        WHERE total_score > :old_total_score
                        """
                    ),
                    {"old_total_score": old_total_score},
                ).scalar_one()
            )

        if new_rank < old_rank:
            db.execute(
                text(
                    """
                    UPDATE leaderboard
                    SET rank = rank + 1
                    WHERE rank >= :new_rank
                      AND rank < :old_rank
                      AND user_id != :user_id
                    """
                ),
                {
                    "new_rank": new_rank,
                    "old_rank": old_rank,
                    "user_id": user_id,
                },
            )

        leaderboard.rank = new_rank

    cache_delete(LEADERBOARD_TOP_CACHE_KEY)
    bump_rank_cache_version()


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
    version = get_rank_cache_version()
    cache_key = f"{PLAYER_RANK_CACHE_KEY_PREFIX}{user_id}:{version}"
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
