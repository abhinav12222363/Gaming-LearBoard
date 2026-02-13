# 🏆 Gaming Leaderboard

A fast, scalable leaderboard system for tracking player scores in real-time. Built with **FastAPI**, **PostgreSQL**, **Redis**, **React**, and **New Relic** for full-stack performance monitoring.

---

## 🚀 Tech Stack

## 📘 Interview Submission

For the second-round review (HLD/LLD, scalability analysis, implemented vs skipped items), see:

- `INTERVIEW_SUBMISSION.md`


| Layer       | Tool/Library                         |
| ----------- | ------------------------------------ |
| Backend API | FastAPI                              |
| Database    | PostgreSQL                           |
| Caching     | Redis                                |
| Frontend    | React + Bootstrap                    |
| Monitoring  | New Relic (APM)                      |
| Logging     | Python logging module (`server.log`) |
| Testing     | Pytest, httpx, TestClient            |
| Deployment  | Localhost (manual), Docker optional  |

---

## 📦 Core Features

| Category          | Feature                                                             |
| ----------------- | ------------------------------------------------------------------- |
| **Gameplay**      | Submit scores, view live top‑10 leaderboard, lookup individual rank |
| **Performance**   | PostgreSQL indexes, Redis caching, async FastAPI routes             |
| **Scalability**   | Handles 1 M+ users / 5 M+ sessions demo dataset                     |
| **Observability** | Structured logging (`server.log`) & New Relic APM                   |
| **Testing**       | Pytest suite (API smoke + cache hit/miss)                           |

---

## 🗄️ Dataset & Load Simulation

### 1. Seed a Large Dataset

Run the SQL below from `psql` to generate **1 M users** and **5 M game sessions** (adjust the `generate_series` ranges if you need a smaller demo):

```sql
-- 1 M users
INSERT INTO users (username)
SELECT 'user_' || generate_series(1, 1000000);

-- 5 M random sessions
INSERT INTO game_sessions (user_id, score, game_mode, timestamp)
SELECT
  floor(random() * 1000000 + 1)::int,
  floor(random() * 10000 + 1)::int,
  CASE WHEN random() > 0.5 THEN 'solo' ELSE 'team' END,
  NOW() - INTERVAL '1 day' * floor(random() * 365)
FROM generate_series(1, 5000000);

-- Bootstrap leaderboard table
INSERT INTO leaderboard (user_id, total_score, rank)
SELECT user_id,
       SUM(score)  AS total_score,
       RANK() OVER (ORDER BY SUM(score) DESC)
FROM game_sessions
GROUP BY user_id;
```

> **Indexing** – creation scripts automatically add indexes on `leaderboard(total_score DESC)` and `game_sessions(user_id)` for O(log n) reads.

### 2. Simulate Continuous Traffic

A quick Python script (`simulate_load.py`) is included. Run:

```bash
python simulate_load.py  # submits scores & polls APIs every 0.5‑2 s
```

The script:

* Randomly submits new scores for existing users
* Calls `/api/leaderboard/top` and `/rank/{id}`
* Validates latency stays sub‑50 ms (visible in New Relic)

---

## 🚦 Performance & Consistency

* **Caching** – Redis stores the top‑10 list & per‑player rank (30 s TTL). Writes invalidate keys atomically.
* **Transactions** – All DB updates use SQLAlchemy sessions (`commit()` boundaries) to ensure atomicity.
* **Indexes** – `leaderboard(total_score DESC)` speeds ranking; `game_sessions(user_id)` speeds aggregation.
* **Concurrency** – FastAPI async endpoints + PostgreSQL row‑level locks prevent race conditions.

---

## 📂 Project Structure

```
Gaming-LearBoard/
└── GameLeaderBoard-main/
    ├── leaderboard-ui/              # Frontend (React + Vite)
    │   ├── public/
    │   ├── src/
    │   │   ├── App.jsx
    │   │   ├── main.jsx
    │   │   └── components/
    │   ├── index.html
    │   ├── package.json
    │   ├── package-lock.json
    │   ├── vite.config.js
    │   └── eslint.config.js
    │
    ├── tests/                        # Backend unit tests
    │   └── test_main.py
    │
    ├── main.py                      # FastAPI entry point
    ├── database.py                  # PostgreSQL connection & session
    ├── models.py                    # SQLAlchemy models
    ├── schemas.py                   # Pydantic request/response schemas
    ├── crud.py                      # Business logic (score submit, rank calc)
    ├── cache.py                     # Redis caching utilities
    │
    ├── newrelic.ini                 # New Relic APM configuration
    ├── requirements.txt             # Python dependencies
    ├── REQUIREMENTS_AUDIT.md        # Dependency audit notes
    ├── INTERVIEW_SUBMISSION.md      # HLD/LLD + design decisions
    ├── README.md                    # Project documentation
    ├── .gitignore
    └── .env                         # Environment variables (NOT committed)

```

---

## ⚙️ Setup Instructions

1. **Clone the repo:**

```bash
git clone https://github.com/LetsGetStartedWithBub/GameLeaderBoard
cd leaderboard
```

2. **Create and activate virtualenv:**

```bash
python3 -m venv lbenv
source lbenv/bin/activate
```

3. **Install requirements:**

```bash
pip install -r requirements.txt
```

4. **Start PostgreSQL and Redis:**

Make sure `leaderboard` DB is created and Redis is running.

5. **Run Backend API:**

```bash
export NEW_RELIC_CONFIG_FILE=newrelic.ini
newrelic-admin run-program uvicorn main:app --reload
```

6. **Run Frontend (React):**

```bash
cd leaderboard-ui
npm install
npm start
```

---

## 🧪 Running Tests

Install test dependencies:

```bash
pip install "httpx[http2]" asgi-lifespan pytest pytest-asyncio
```

Run tests:

```bash
pytest
```

---

## 📊 Logging

All HTTP requests and responses are logged to:

* Terminal (`stdout`)
* `server.log` (persistent file)

Example entry:

```
2025-07-03 18:22:30,932 - INFO - Incoming request: GET /api/leaderboard/top
2025-07-03 18:22:30,934 - INFO - Completed with status code: 200
```

---

## 📈 Monitoring

This app is integrated with **New Relic APM**:

* Real-time metrics: throughput, latency, error rate
* Transaction traces per endpoint
* Logs forwarded to New Relic (optional)

Access dashboard: [https://one.newrelic.com/](https://one.newrelic.com/)
![WhatsApp Image 2026-02-13 at 1 51 45 PM](https://github.com/user-attachments/assets/50cf2636-fd9c-42cb-9f9a-d364fbdb3e3b)
![WhatsApp Image 2026-02-13 at 1 51 16 PM](https://github.com/user-attachments/assets/5e0a1827-ff53-4289-8bb3-a2bd19487796)
![WhatsApp Image 2026-02-13 at 1 53 07 PM](https://github.com/user-attachments/assets/fc6af298-629b-4422-bfce-1136fb8f4de2)
![WhatsApp Image 2026-02-13 at 1 51 02 PM](https://github.com/user-attachments/assets/119b13b5-8550-4dc9-a6b4-53d4f0640fda)



---

## 💡 Notes

* Leaderboard data is cached using Redis for fast access.
* Ranks update in near real-time without recomputing the whole board.
* Frontend auto-refreshes leaderboard every 10 seconds.

---

## ✅ Status Summary

| Feature                 | Status |
| ----------------------- | ------ |
| Leaderboard API         | ✅ Done |
| Redis cache integration | ✅ Done |
| Rank computation        | ✅ Done |
| New Relic observability | ✅ Done |
| Logging                 | ✅ Done |
| Unit tests              | ✅ Done |
| Auto-refresh UI         | ✅ Done |
| Submit Score frontend   | ✅ Done |
| Bootstrap UI            | ✅ Done |

---


## 🎯 Interview Alignment Notes (Important)

### 1) API path parity
The backend exposes the exact assignment paths:

- `POST /api/leaderboard/submit`
- `GET /api/leaderboard/top`
- `GET /api/leaderboard/rank/{id}`

### 2) Ranking strategy: **SUM vs AVG**
This implementation intentionally uses **SUM(score)** semantics via `leaderboard.total_score` and rank ordering by `total_score DESC`.

Why SUM here:
- It matches the assignment phrase “highest total score”.
- It rewards sustained performance across many sessions.
- It is efficient for write-time incremental updates (`total_score += score`) without full re-aggregation.

When AVG would be better:
- If product requirements prioritize “consistency per session” over total accumulation.
- If users play very different numbers of rounds and fairness needs normalization.

### 3) Cache invalidation strategy
Current behavior follows a **cache-aside/read-through** style:
- Reads (`/top`, `/rank/{id}`): check Redis first; on miss, query DB and set cache.
- Writes (`/submit`): commit DB transaction first, then invalidate affected keys.

Design details:
- TTL is 30 seconds for top leaderboard and player rank keys.
- Write-time invalidation keeps stale windows short and bounded by the next read + TTL.
- Under concurrent writes, DB remains source of truth; cache is eventually consistent and self-heals on misses.

### 4) Atomicity and race-condition handling
`submit_score` runs in a single DB transaction (`with db.begin():`) so user creation, session insert, and leaderboard update either all commit or all roll back.

To reduce lost updates under concurrent writes, leaderboard rows are read with `FOR UPDATE` before applying `total_score += score`, ensuring serial updates for the same player row.

This gives:
- Atomic writes for a submit operation.
- Consistent score accumulation under concurrency.
- Deterministic rank recomputation because rank queries always read committed totals.

  ---

## 🎥 Demo Video

A complete working demo of the Gaming Leaderboard system (backend APIs, frontend UI, Redis caching, and New Relic monitoring) is available here:

🔗 **Demo Link:**  
https://drive.google.com/file/d/1gv1Y95NghYZzg2ewesDRnY7Pei1SQBUH/view?usp=sharing

The demo showcases:
- Score submission flow
- Live leaderboard updates
- Player rank lookup
- Redis-backed low-latency responses
- New Relic performance monitoring dashboards

