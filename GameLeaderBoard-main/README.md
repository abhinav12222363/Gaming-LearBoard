# 🏆 Gaming Leaderboard

A fast, scalable leaderboard system for tracking player scores in real-time. Built with **FastAPI**, **PostgreSQL**, **Redis**, **React**, and **New Relic** for full-stack performance monitoring.

---

## 🚀 Tech Stack

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
leaderboard/
├── main.py             # FastAPI entry point
├── database.py         # PostgreSQL DB connection
├── models.py           # SQLAlchemy models
├── crud.py             # Business logic
├── schemas.py          # Pydantic request/response models
├── utils.py            # Redis utilities
├── tests/              # Pytest test cases
│   └── test_main.py
├── server.log          # Log output
├── newrelic.ini        # New Relic config
└── requirements.txt
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
<img width="1710" alt="Screenshot 2025-07-03 at 10 22 40 PM" src="https://github.com/user-attachments/assets/11b7605a-bc7f-4330-a490-a0e475f2895c" />
<img width="1710" alt="Screenshot 2025-07-03 at 10 22 55 PM" src="https://github.com/user-attachments/assets/e2292be9-39ff-40cb-b85f-9bb128d8688f" />
<img width="1710" alt="Screenshot 2025-07-03 at 10 23 11 PM" src="https://github.com/user-attachments/assets/a8610961-daa6-490d-8bd9-0859b266eba9" />


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
