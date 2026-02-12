import React, { useState } from 'react';
import axios from 'axios';

const ScoreSubmit = ({ onSubmitSuccess }) => {
  const [userId, setUserId] = useState('');
  const [score, setScore] = useState('');
  const [message, setMessage] = useState('');

  const handleSubmit = async () => {
    try {
      await axios.post('http://localhost:8000/api/leaderboard/submit', {
        user_id: parseInt(userId),
        score: parseInt(score),
      });

      setMessage('✅ Score submitted successfully!');
      setUserId('');
      setScore('');

      if (onSubmitSuccess) onSubmitSuccess(); // Refresh leaderboard after submission
    } catch (err) {
      console.error(err);
      setMessage('❌ Failed to submit score.');
    }
  };

  return (
    <div className="card mb-4">
      <div className="card-body">
        <h5 className="card-title">Submit New Score</h5>
        <div className="mb-3">
          <input
            type="number"
            className="form-control"
            placeholder="User ID"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
          />
        </div>
        <div className="mb-3">
          <input
            type="number"
            className="form-control"
            placeholder="Score"
            value={score}
            onChange={(e) => setScore(e.target.value)}
          />
        </div>
        <button className="btn btn-success" onClick={handleSubmit}>
          Submit Score
        </button>

        {message && <div className="mt-3 alert alert-info">{message}</div>}
      </div>
    </div>
  );
};

export default ScoreSubmit;
