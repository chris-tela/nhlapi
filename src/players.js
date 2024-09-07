import React, { useEffect, useState } from 'react';
import { getPlayerData } from './service.js';

// src/components/Teams.js

const Players = () => {
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getPlayerData();
        if (Array.isArray(data["query"])) {
          setPlayers(data["query"]);
          console.log(data["query"]);
        } else {
          setError('Data format is incorrect');
        }
      } catch (error) {
        setError('Error fetching player data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <p>Loading player data...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div>
      <h2>Players</h2>
      {players.length > 0 ? (
        <ul>
          {players.map((player, index) => (
            <li key={index}>{player.name}</li> 
          ))}
        </ul>
      ) : (
        <p>No players found.</p>
      )}
    </div>
  );
};

export default Players;
