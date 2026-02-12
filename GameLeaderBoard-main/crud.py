from sqlalchemy.orm import Session
from models import GameSession, Leaderboard
from sqlalchemy import func
from schemas import PlayerRank
from cache import cache_get, cache_set  # ✅ new import

def submit_score(db: Session, user_id: int, score: int):
    from models import User, GameSession, Leaderboard

    # ✅ Step 1: Check if user exists, else create
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        user = User(id=user_id, username=f"user_{user_id}")
        db.add(user)
        db.commit()

    # ✅ Step 2: Save new game session
    session = GameSession(user_id=user_id, score=score, game_mode="solo")
    db.add(session)
    db.commit()

    # ✅ Step 3: Update leaderboard
    leaderboard = db.query(Leaderboard).filter_by(user_id=user_id).first()
    if leaderboard:
        leaderboard.total_score += score
    else:
        leaderboard = Leaderboard(user_id=user_id, total_score=score)
        db.add(leaderboard)
    db.commit()

    # ✅ Step 4: Invalidate cache
    cache_set(f"player_rank_{user_id}", None, ex=1)
    cache_set("leaderboard_top_10", None, ex=1)


def get_top_leaderboard(db: Session):
    cache_key = "leaderboard_top_10"
    cached = cache_get(cache_key)
    if cached:
        return cached

    top_players = db.query(Leaderboard).order_by(Leaderboard.total_score.desc()).limit(10).all()
    result = [
        {"user_id": p.user_id, "total_score": p.total_score, "rank": p.rank}
        for p in top_players
    ]
    cache_set(cache_key, result, ex=30)
    return result


def get_player_rank(db: Session, user_id: int):
    cache_key = f"player_rank_{user_id}"
    cached = cache_get(cache_key)
    if cached:
        return PlayerRank(**cached)

    subquery = db.query(
        Leaderboard.user_id,
        Leaderboard.total_score,
        func.rank().over(order_by=Leaderboard.total_score.desc()).label("rank")
    ).subquery()

    result = db.query(subquery).filter(subquery.c.user_id == user_id).first()
    if result:
        player = PlayerRank(user_id=result.user_id, total_score=result.total_score, rank=result.rank)
        cache_set(cache_key, player.dict(), ex=30)
        return player

    return PlayerRank(user_id=user_id, total_score=0, rank=-1)
