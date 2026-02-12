import React, { useEffect, useState } from 'react';
import axios from 'axios';

const LeaderboardTable = () => {
  const [topPlayers, setTopPlayers] = useState([]);

  useEffect(() => {
    fetchTopPlayers();

    const interval = setInterval(fetchTopPlayers, 10000); // every 10s
    return () => clearInterval(interval);
  }, []);

  const fetchTopPlayers = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/leaderboard/top');
      setTopPlayers(res.data);
    } catch (err) {
      console.error('Failed to fetch leaderboard:', err);
    }
  };

  return (
    <div>
      <h3 className="mb-3">Top 10 Players</h3>
      <table className="table table-striped table-bordered">
        <thead className="table-light">
          <tr>
            <th>Rank</th>
            <th>User ID</th>
            <th>Total Score</th>
          </tr>
        </thead>
        <tbody>
          {topPlayers.map((player, index) => (
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
};

export default LeaderboardTable;
