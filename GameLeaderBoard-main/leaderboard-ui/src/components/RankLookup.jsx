import React, { useState } from 'react';
import axios from 'axios';

const RankLookup = () => {
  const [userId, setUserId] = useState('');
  const [rankInfo, setRankInfo] = useState(null);
  const [error, setError] = useState('');

  const fetchRank = async () => {
    if (!userId) return;

    try {
      const res = await axios.get(`http://localhost:8000/api/leaderboard/rank/${userId}`);
      setRankInfo(res.data);
      setError('');
    } catch (err) {
      setError('User not found');
      setRankInfo(null);
    }
  };

  return (
    <div className="card">
      <div className="card-body">
        <h5 className="card-title mb-3">Check Player Rank</h5>
        <div className="input-group mb-3">
          <input
            type="number"
            className="form-control"
            placeholder="Enter User ID"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
          />
          <button className="btn btn-primary" onClick={fetchRank}>Search</button>
        </div>

        {rankInfo && (
          <div className="alert alert-success">
            <p><strong>User ID:</strong> {rankInfo.user_id}</p>
            <p><strong>Rank:</strong> {rankInfo.rank}</p>
            <p><strong>Total Score:</strong> {rankInfo.total_score}</p>
          </div>
        )}

        {error && <div className="alert alert-danger">{error}</div>}
      </div>
    </div>
  );
};

export default RankLookup;
