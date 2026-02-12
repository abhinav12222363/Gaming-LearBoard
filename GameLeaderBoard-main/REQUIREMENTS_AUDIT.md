# Assignment Requirements Audit

## Scope
This audit checks whether the current repository satisfies the stated take-home assignment requirements for:
- backend APIs
- scale/readiness for large datasets
- monitoring
- latency optimization
- atomicity/consistency
- frontend live updates
- testing, security, and documentation deliverables

## Verdict
**Current status: partially complete; it does not yet meet all requirements end-to-end.**

## Requirement-by-requirement checklist

### 0) Basic APIs setup

| Requirement | Status | Notes |
|---|---|---|
| `POST /api/leaderboard/submit` | ✅ Implemented | Endpoint exists and writes score via CRUD logic. |
| `GET /api/leaderboard/top` | ✅ Implemented | Endpoint returns top players with rank from SQL window function. |
| `GET /api/leaderboard/rank/{user_id}` | ⚠️ Partial | Implemented as `/rank/{id}` (works functionally, path variable name differs). |

### 1) Setup database with large dataset

| Requirement | Status | Notes |
|---|---|---|
| Provide/execute seed flow for 1M users + 5M sessions | ⚠️ Partial | SQL is documented in README, but there is no versioned SQL migration/seed script in repo for reproducible setup. |

### 2) Simulate real user usage

| Requirement | Status | Notes |
|---|---|---|
| Include and run Python load simulation script | ❌ Missing | README references `simulate_load.py`, but this file is not present. |

### 3) New Relic monitoring

| Requirement | Status | Notes |
|---|---|---|
| New Relic integration in app | ✅ Implemented | App initializes New Relic when config env var is present. |
| Monitoring analysis/report/screenshots | ⚠️ Partial | README embeds screenshots, but there is no structured performance report artifact in repo. |
| Alerting setup evidence | ❌ Missing | No alert policy/config evidence is checked into repository. |

### 4) Optimize API latency

| Requirement | Status | Notes |
|---|---|---|
| Indexing | ⚠️ Partial | README claims indexes, but no explicit migration/DDL for indexes is versioned. |
| Caching | ✅ Implemented | Redis cache for top leaderboard and player rank with TTL + invalidation exists. |
| Query optimization | ⚠️ Partial | Uses window queries; no benchmark evidence or EXPLAIN plans committed. |
| Concurrency handling | ✅ Implemented | Row-level lock (`FOR UPDATE`) used for leaderboard row updates. |
| Demonstrated latency reduction | ❌ Missing | No before/after measurements or benchmark report committed. |

### 5) Ensure atomicity and consistency

| Requirement | Status | Notes |
|---|---|---|
| Transactional writes | ✅ Implemented | `submit_score` wraps user/session/leaderboard writes in a single transaction. |
| Cache invalidation strategy | ✅ Implemented | Invalidates top-10 and impacted player rank keys after commit. |
| Consistency under high traffic proof | ⚠️ Partial | Correct mechanisms exist, but no stress-test proof/results in repo. |

### 6) Build frontend UI with live updates

| Requirement | Status | Notes |
|---|---|---|
| Top-10 leaderboard display | ✅ Implemented | React UI displays table and polls API every 10s. |
| User rank lookup | ✅ Implemented | Rank lookup component is implemented in UI. |
| Live updates | ✅ Implemented | Auto-refresh polling (10s interval) is present. |

### Evaluation and deliverables

| Requirement | Status | Notes |
|---|---|---|
| Bug-free working | ⚠️ Partial | Tests fail in this environment because DB is required at import time. |
| Code quality/modularity | ✅ Implemented | Project separated into models/schemas/crud/cache layers. |
| Unit tests | ⚠️ Partial | Basic API tests exist; no concurrency/performance tests and no DB-isolated test setup. |
| Basic API security | ❌ Missing | No auth/rate limiting/input constraints beyond basic typing. |
| Performance report | ❌ Missing | No committed report with metrics/analysis. |
| Documentation | ⚠️ Partial | README is detailed but includes claims not fully backed by committed artifacts (e.g., missing load script). |
| HLD/LLD | ❌ Missing | No dedicated HLD/LLD docs located in repo. |

## High-priority gaps to close
1. Add reproducible SQL migrations/seed scripts (including indexes) and a checked-in load script.
2. Add performance evidence: baseline vs optimized latency, p95/p99, slow-query analysis, and New Relic alert definitions.
3. Improve test strategy: isolated test DB, Redis mocking, concurrency tests for `submit_score`.
4. Add minimal API security controls (input bounds, rate limiting, and optional auth).
5. Add explicit HLD/LLD docs and a concise performance report as required deliverables.

## Security note
`newrelic.ini` currently contains a plaintext license key and should be rotated/revoked and replaced with an environment-variable based secret.
