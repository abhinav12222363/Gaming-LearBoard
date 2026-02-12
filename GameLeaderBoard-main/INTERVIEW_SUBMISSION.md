# Gaming Leaderboard — Second-Round Review (HLD + LLD)

## 1) End-to-end review summary

### Backend (FastAPI + SQLAlchemy)
- API layer is small and clean; routes delegate business logic to `crud.py`.
- `submit_score` runs DB writes in a single transaction boundary (`with db.begin()`), which preserves atomicity.
- Leaderboard data model is **user-based** (one row per user in `leaderboard`), while `game_sessions` keeps append-only audit history.

### Database design
- `leaderboard.user_id` is unique, enforcing one leaderboard row per user.
- `game_sessions` stores every score event, enabling reconciliation and audit.
- Ranking is persisted in `leaderboard.rank` for fast reads.

### Redis usage
- Cache-aside pattern is used:
  - top-10 cache key
  - per-user rank cache key
- Write-path invalidation exists and was refined to avoid O(N) key scans on every write.

### Frontend
- Polling-based “live” updates every 10s.
- Submission and rank lookup work.
- Top table previously rendered `index + 1`; now corrected to render backend rank, including ties.

---

## 2) Correctness checks requested in assignment

## ✅ User-based leaderboard (one row per user)
Implemented and enforced by schema:
- `leaderboard.user_id` is `unique=True` and `nullable=False`.

## ✅ Tie-aware rank semantics
- Rank semantics are now deterministic and tie-safe:
  - rank recomputation SQL uses `RANK() OVER (ORDER BY total_score DESC, user_id ASC)` when invoked.
  - incremental write path computes rank using `COUNT(total_score > user_score) + 1`, which gives identical ranks for ties.

## ✅ Atomicity / concurrency
- `submit_score` contains user creation + session insert + leaderboard update in one transaction.
- `SELECT ... FOR UPDATE` locks the player’s leaderboard row, preventing lost updates for concurrent writes to same user.
- Post-commit cache invalidation keeps DB as source of truth.

## ✅ Redis strategy and invalidation
- Top-10 cache invalidated on writes.
- Per-user rank cache moved to **versioned keys**:
  - read key: `player_rank_{user_id}:{version}`
  - write invalidation: increment global version key
- This avoids expensive `KEYS player_rank_*` scans under load.

---

## 3) Performance optimizations applied

1. **Schema-level indexes/constraints**
   - Added descending composite index for leaderboard scans:
     - `(total_score DESC, user_id ASC)`
   - Indexed `game_sessions.user_id` and `game_sessions.timestamp`.
   - Added non-negative check constraints for `score` and `total_score`.

2. **Avoiding full rank recomputation per submit**
   - Previous flow recalculated ranks for all rows on each write (O(N)).
   - New flow updates only impacted range between `new_rank` and `old_rank`.
   - Improves write scalability significantly for large leaderboards.

3. **Cache invalidation scalability**
   - Replaced broad pattern-delete dependency for per-user rank invalidation with version bump.
   - Eliminates O(number_of_rank_keys) invalidation cost.

---

## 4) 1M users / 5M sessions scalability discussion

### What scales well now
- Read path for top-10 is fast due to:
  - persisted rank
  - rank/top cache
  - leaderboard ordering index
- Write path no longer does full-table rank recompute on every submit.
- Append-only `game_sessions` supports analytical backfills and audit.

### Remaining trade-offs / limits
- Persisting rank in-row still needs shifting a rank range on score changes; hot, high-churn workloads can produce write amplification.
- Versioned rank cache is eventually consistent and may leave old-version keys until TTL expiry (intentional memory vs CPU trade-off).
- Global rank updates are still more expensive than purely computed-on-read rank systems.

### Next-step options (if asked in interview)
- Replace persisted rank with computed rank for top-N and specific user using indexed score lookups.
- Keep only `total_score` in primary table and materialize rank periodically/asynchronously.
- Move “near real-time” push to WebSocket/SSE with pub/sub fanout.
- Partition `game_sessions` by time for long-term growth.

---

## 5) Frontend review

- Top leaderboard display now shows `player.rank`, so ties render correctly.
- Auto-refresh every 10 seconds gives “near-live” behavior.
- Rank lookup remains direct and simple.

---

## 6) What is implemented vs intentionally skipped

## Implemented
- Tie-correct ranking behavior on backend and UI display.
- Better write-path complexity by avoiding full-rank recomputation per submit.
- Concurrency-safe score update transaction with row locking.
- Scalable cache invalidation strategy (versioned per-user rank keys).
- Indexes + constraints for correctness/performance.

## Intentionally skipped
- Full WebSocket real-time streaming.
- Background ranking workers / materialized view pipeline.
- Online migration scripts (Alembic) in this patch.

## Why skipped
- Assignment asks for minimal, high-impact improvements without rewriting project.
- Current updates maximize correctness/scalability delta while keeping architecture and APIs stable.
