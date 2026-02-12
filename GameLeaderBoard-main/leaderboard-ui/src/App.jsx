import React, { useEffect, useState } from 'react';
import axios from 'axios';
import ScoreSubmit from './components/ScoreSubmit';

function App() {
  const [leaderboard, setLeaderboard] = useState([]);
  const [userId, setUserId] = useState('');
  const [rankData, setRankData] = useState(null);
  const [error, setError] = useState('');

  const fetchTop = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/leaderboard/top');
      setLeaderboard(res.data);
    } catch (err) {
      console.error('Error fetching leaderboard:', err);
    }
  };

  const handleSearch = async () => {
    try {
      const res = await axios.get(`http://localhost:8000/api/leaderboard/rank/${userId}`);
      setRankData(res.data);
      setError('');
    } catch (err) {
      setError('User not found');
      setRankData(null);
    }
  };

  useEffect(() => {
    fetchTop();
    const interval = setInterval(fetchTop, 10000); // auto-refresh every 10s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="container mt-5">
      <h1 className="text-center mb-4">🏆 Gaming Leaderboard</h1>

      {/* Submit Score Section */}
      <ScoreSubmit onSubmitSuccess={fetchTop} />

      {/* Search Player Rank */}
      <div className="card mb-4">
        <div className="card-body">
          <h5 className="card-title">Search Player Rank</h5>
          <div className="input-group">
            <input
              type="number"
              className="form-control"
              placeholder="Enter User ID"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
            />
            <button className="btn btn-primary" onClick={handleSearch}>
              Search
            </button>
          </div>

          {rankData && (
            <div className="mt-3 alert alert-success">
              <p><strong>User ID:</strong> {rankData.user_id}</p>
              <p><strong>Rank:</strong> {rankData.rank}</p>
              <p><strong>Total Score:</strong> {rankData.total_score}</p>
            </div>
          )}

          {error && <div className="mt-3 alert alert-danger">{error}</div>}
        </div>
      </div>

      {/* Leaderboard Table */}
      <table className="table table-bordered table-striped">
        <thead className="table-light">
          <tr>
            <th>Rank</th>
            <th>User ID</th>
            <th>Total Score</th>
          </tr>
        </thead>
        <tbody>
          {leaderboard.map((player, index) => (
            <tr key={player.user_id}>
              <td>{index + 1}</td>
              <td>{player.user_id}</td>
              <td>{player.total_score}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;
