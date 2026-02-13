
🏆 Gaming Leaderboard System

A scalable, real-time Gaming Leaderboard built as part of a take-home assignment, designed to handle high traffic, large datasets, and provide full observability using New Relic.

This system allows players to submit scores, view top rankings, and check individual ranks with low latency and strong consistency guarantees.

🚀 Tech Stack
Layer	Technology
Backend API	FastAPI
Database	PostgreSQL
Caching	Redis
Frontend	React + Bootstrap
Monitoring	New Relic APM
Logging	Python logging
Testing	Pytest
Deployment	Localhost (Docker optional)
📌 Assignment Requirements Coverage

✅ Submit Score API
✅ Top 10 Leaderboard API
✅ Player Rank API
✅ Large dataset handling (1M+ users)
✅ Concurrency-safe writes
✅ Redis caching
✅ New Relic monitoring
✅ Frontend with live updates

🔗 API Endpoints
Method	Endpoint	Description
POST	/api/leaderboard/submit	Submit a player score
GET	/api/leaderboard/top	Get top 10 players
GET	/api/leaderboard/rank/{user_id}	Get rank of a user
🗄️ Database Schema
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

📊 Large Dataset Setup (Assignment Requirement)

⚠️ Run manually in PostgreSQL (not auto-run by backend)

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

🔄 Load Simulation (Real User Traffic)
import requests, random, time

API = "http://localhost:8000/api/leaderboard"

while True:
    uid = random.randint(1, 1000000)
    requests.post(f"{API}/submit", json={"user_id": uid, "score": random.randint(100, 10000)})
    requests.get(f"{API}/top")
    requests.get(f"{API}/rank/{uid}")
    time.sleep(random.uniform(0.5, 2))

⚡ Performance & Consistency Design
🔹 Ranking Strategy

Uses SUM(score) (matches “highest total score” requirement)

Ranks computed via SQL RANK() → supports ties

🔹 Atomic Writes

Score submission runs in single DB transaction

Uses row-level locks (FOR UPDATE) to prevent race conditions

🔹 Redis Caching

Top-10 leaderboard cached (TTL 30s)

Player rank cached per user

Write operations invalidate affected keys

🔹 Indexing

leaderboard(total_score DESC)

game_sessions(user_id)

📈 Monitoring with New Relic

Integrated New Relic Python APM to track:

API latency

Error rate

Throughput

PostgreSQL & Redis query time

Dashboard available in New Relic UI
![WhatsApp Image 2026-02-13 at 1 51 16 PM](https://github.com/user-attachments/assets/24562374-a979-4250-8c37-c6c1af924b82)


🧪 Testing
pip install pytest httpx pytest-asyncio
pytest


Tests validate:

API correctness

Cache hit/miss behavior

Error handling

🖥️ Frontend (React)

Features:

Submit score

Live top-10 leaderboard

Player rank lookup

Auto-refresh every 10 seconds

cd leaderboard-ui
npm install
npm start

📂 Project Structure
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

🔐 Security Notes

.env and license keys are not committed

New Relic key loaded via environment variable

CORS restricted to frontend origin

✅ Final Status
Feature	Status
Backend APIs	✅
Redis caching	✅
Large dataset support	✅
Concurrency handling	✅
New Relic monitoring	✅
Frontend UI	✅
Load simulation	✅
