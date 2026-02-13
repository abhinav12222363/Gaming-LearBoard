# 🏆 Gaming Leaderboard System

A scalable, real-time **Gaming Leaderboard** built for a take-home assignment.

It supports:
- score submissions,
- top player rankings,
- per-player rank lookups,
- high-traffic read performance,
- observability with New Relic.

---

## 🚀 Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI |
| Database | PostgreSQL |
| Caching | Redis |
| Frontend | React + Bootstrap |
| Monitoring | New Relic APM |
| Logging | Python `logging` |
| Testing | Pytest |
| Deployment | Localhost (Docker optional) |

---

## 📌 Assignment Requirements Coverage

- ✅ Submit Score API
- ✅ Top-10 Leaderboard API
- ✅ Player Rank API
- ✅ Large dataset handling (1M+ users)
- ✅ Concurrency-safe writes
- ✅ Redis caching
- ✅ New Relic monitoring
- ✅ Frontend with live updates

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/leaderboard/submit` | Submit a player score |
| `GET` | `/api/leaderboard/top` | Get top-10 players |
| `GET` | `/api/leaderboard/rank/{user_id}` | Get rank of a user |

**Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🗄️ Database Schema

```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(255) UNIQUE NOT NULL,
  join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE game_sessions (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id) ON DELETE CASCADE,
  score INT NOT NULL,
  game_mode VARCHAR(50) NOT NULL,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE leaderboard (
  id SERIAL PRIMARY KEY,
  user_id INT UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  total_score INT NOT NULL,
  rank INT
);
```

---

## 📊 Large Dataset Setup (Manual)

> ⚠️ Run this manually in PostgreSQL. It is **not** auto-run by the backend.

```sql
-- 1M users
INSERT INTO users (username)
SELECT 'user_' || generate_series(1, 1000000);

-- 5M game sessions
INSERT INTO game_sessions (user_id, score, game_mode, timestamp)
SELECT
  floor(random() * 1000000 + 1)::int,
  floor(random() * 10000 + 1)::int,
  CASE WHEN random() > 0.5 THEN 'solo' ELSE 'team' END,
  NOW() - INTERVAL '1 day' * floor(random() * 365)
FROM generate_series(1, 5000000);

-- Bootstrap leaderboard
INSERT INTO leaderboard (user_id, total_score, rank)
SELECT
  user_id,
  SUM(score) AS total_score,
  RANK() OVER (ORDER BY SUM(score) DESC)
FROM game_sessions
GROUP BY user_id;
```

**Recommended indexes:**
- `leaderboard(total_score DESC)`
- `game_sessions(user_id)`

---

## ⚡ Performance & Consistency Design

### Ranking strategy
- Uses `SUM(score)` to satisfy the **highest total score** requirement.
- Uses SQL `RANK()` to support ties.

### Atomic writes
- Score submission executes in a **single DB transaction**.
- Uses row-level locks (`FOR UPDATE`) to prevent race conditions.

### Redis caching
- Top-10 leaderboard is cached (TTL: 30s).
- Player rank is cached per user.
- Write operations invalidate affected cache keys.

---

## 📈 Monitoring with New Relic

The project integrates New Relic Python APM to track:
- API latency,
- error rate,
- throughput,
- PostgreSQL query time,
- Redis cache performance.

Live dashboards are available in New Relic UI.

![New Relic Dashboard 1](https://github.com/user-attachments/assets/7823ecc5-ecbb-4dea-a5de-b1c6c5e2f816)
![New Relic Dashboard 2](https://github.com/user-attachments/assets/7feca7f7-059e-4014-8ccd-900eb5f4dd96)
![New Relic Dashboard 3](https://github.com/user-attachments/assets/73d25f27-09d5-4242-a12c-4991d73851a0)

---

## ⚙️ Setup Instructions

### 1) Clone repository

```bash
git clone https://github.com/<your-username>/GameLeaderBoard
cd GameLeaderBoard-main
```

### 2) Create virtual environment

```bash
python -m venv venv
```

### 3) Activate virtual environment

**Windows**
```bash
venv\Scripts\activate
```

**Linux / macOS**
```bash
source venv/bin/activate
```

---

## 📂 Project Structure

```text
GameLeaderBoard-main/
├── main.py
├── database.py
├── models.py
├── crud.py
├── schemas.py
├── cache.py
├── requirements.txt
├── newrelic.ini
├── tests/
├── leaderboard-ui/
└── README.md
```

---

## 🔐 Security Notes

- `.env` and license keys are not committed.
- New Relic key is loaded via environment variable.
- CORS is restricted to frontend origin.

---

## ✅ Final Status

| Feature | Status |
|---|---|
| Backend APIs | ✅ |
| Redis caching | ✅ |
| Large dataset support | ✅ |
| Concurrency handling | ✅ |
| New Relic monitoring | ✅ |
| Frontend UI | ✅ |
| Load simulation | ✅ |
