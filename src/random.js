import React, { useEffect, useState } from 'react';
import { getAllPlayers, getRandomPlayer, getPlayerData } from './service.js';
import './styles.css';

const Random = () => {
    const [player, setPlayer] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [guess, setGuess] = useState('');
    const [feedback, setFeedback] = useState('');
    const [posFeedback, setPosFeedback] = useState('');
    const [allPlayers, setAllPlayers] = useState([]);
    const [suggestions, setSuggestions] = useState([]);
    const [pastGuesses, setPastGuesses] = useState([]);
    const [guessCount, setGuessCount] = useState(0);
    const [gameOver, setGameOver] = useState(false);
    const [showPopup, setShowPopup] = useState(false);
    const [winner, setWinner] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const data = await getRandomPlayer();
                setPlayer(data["player"]);
                console.log(data["player"]);
                const playersList = await getAllPlayers();
                setAllPlayers(playersList["names"]);
            } catch (error) {
                setError('Error fetching player data');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    const handleGuessChange = (e) => {
        const value = e.target.value;
        setGuess(value);

        const filteredSuggestions = allPlayers.filter(player =>
            player.toLowerCase().includes(value.toLowerCase())
        );

        setSuggestions(filteredSuggestions);
    };

    const handleSuggestionClick = (suggestion) => {
        setGuess(suggestion);
        setSuggestions([]);
    };

    const handleGuessSubmit = async () => {
        if (guessCount < 7 && !gameOver) {
            const guessedPlayer = allPlayers.find(p => p.toLowerCase() === guess.toLowerCase());

            if (!guessedPlayer) {
                setFeedback('Player not found.');
                return;
            }

            const playerDb = await getPlayerData();
            let guessedPlayerData;
            for (let i = 0; i < playerDb["query"].length; i++) {
                if (guessedPlayer === playerDb["query"][i]["name"]) {
                    guessedPlayerData = playerDb["query"][i];
                    break;
                }
            }

            const isCorrect = guessedPlayerData.name.toLowerCase() === player.name.toLowerCase();

            const newGuess = {
                name: guessedPlayerData.name,
                team: guessedPlayerData.past_teams.slice(-1).join(', '),
                goals: guessedPlayerData.goals,
                assists: guessedPlayerData.assists,
                age: guessedPlayerData.age,
                height: guessedPlayerData.height,
                country: guessedPlayerData.country,
                position: guessedPlayerData.position,
                conference: guessedPlayerData.conference,
                division: guessedPlayerData.division,
                correct: isCorrect,
                cellStyles: {
                    team: guessedPlayerData.past_teams.slice(-1).join(', ') === player.past_teams.slice(-1).join(', ') ? (isCorrect ? 'correct-cell' : 'past-team-cell') : (player.past_teams.includes(guessedPlayerData.past_teams.slice(-1).join(', ')) ? 'past-team-cell' : 'incorrect-cell'),
                    goals: guessedPlayerData.goals === player.goals ? 'correct-cell' : 'incorrect-cell',
                    assists: guessedPlayerData.assists === player.assists ? 'correct-cell' : 'incorrect-cell',
                    age: guessedPlayerData.age === player.age ? 'correct-cell' : 'incorrect-cell',
                    height: guessedPlayerData.height === player.height ? 'correct-cell' : 'incorrect-cell',
                    country: guessedPlayerData.country === player.country ? 'correct-cell' : 'incorrect-cell',
                    position: guessedPlayerData.position === player.position ? 'correct-cell' : 'incorrect-cell',
                    conference: guessedPlayerData.conference === player.conference ? 'correct-cell' : 'incorrect-cell',
                    division: guessedPlayerData.division === player.division ? 'correct-cell' : 'incorrect-cell'
                }
            };

            setPastGuesses([...pastGuesses, newGuess]);

            setGuessCount(guessCount + 1);

            if (isCorrect) {
                setPosFeedback('Correct! You guessed the player.');
                setGameOver(true);
                setWinner(guessedPlayerData);
                setShowPopup(true);
            } else if (guessCount === 6) {
                setFeedback(`Incorrect. You've used all your guesses. The player was ${player.name}.`);
                setGameOver(true);
            } else {
                setFeedback('Incorrect, try again.');
            }

            setGuess('');
            setSuggestions([]);
        }
    };

    const handlePopupClose = () => {
        setShowPopup(false);
        setWinner(null);
    };

    if (loading) return <p>Loading player data...</p>;
    if (error) return <p>{error}</p>;

    return (
        <div className="container">
            <h2>Mystery Player</h2>

            <div className="input-container">
                <h3>Guess the Player's Name (Guesses Left: {7 - guessCount}):</h3>
                <input
                    type="text"
                    value={guess}
                    onChange={handleGuessChange}
                    placeholder="Enter player's name"
                    disabled={gameOver || guessCount >= 7}
                />
                <button onClick={handleGuessSubmit} disabled={gameOver || guessCount >= 7}>
                    Submit Guess
                </button>
            </div>

            {suggestions.length > 0 && (
                <ul className="suggestions-list">
                    {suggestions.map((suggestion, index) => (
                        <li
                            key={index}
                            onClick={() => handleSuggestionClick(suggestion)}
                        >
                            {suggestion}
                        </li>
                    ))}
                </ul>
            )}

            {feedback && <p className="feedback-message">{feedback}</p>}
            {posFeedback && <p className="posFeedback-message"> {posFeedback} </p>}

            {pastGuesses.length > 0 && (
                <div className="chart-container">
                    <table className="chart-table">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Team</th>
                                <th>Goals</th>
                                <th>Assists</th>
                                <th>Age</th>
                                <th>Height</th>
                                <th>Country</th>
                                <th>Position</th>
                                <th>Conference</th>
                                <th>Division</th>
                            </tr>
                        </thead>
                        <tbody>
                            {pastGuesses.map((pastGuess, index) => (
                                <tr key={index} className={pastGuess.correct ? 'correct' : ''}>
                                    <td className={pastGuess.correct ? 'bold-cell' : ''}>{pastGuess.name}</td>
                                    <td className={pastGuess.cellStyles.team}>{pastGuess.team}</td>
                                    <td className={pastGuess.cellStyles.goals}>
                                        {pastGuess.goals}
                                        {pastGuess.goals < player.goals && <span className="arrow-up"> ↑ </span>}
                                        {pastGuess.goals > player.goals && <span className="arrow-down"> ↓ </span>}
                                    </td>
                                    <td className={pastGuess.cellStyles.assists}>
                                        {pastGuess.assists}
                                        {pastGuess.assists < player.assists && <span className="arrow-up"> ↑ </span>}
                                        {pastGuess.assists > player.assists && <span className="arrow-down"> ↓ </span>}
                                    </td>
                                    <td className={pastGuess.cellStyles.age}>
                                        {pastGuess.age}
                                        {pastGuess.age < player.age && <span className="arrow-down"> ↓ </span>}
                                        {pastGuess.age > player.age && <span className="arrow-up"> ↑ </span>}
                                    </td>
                                    <td className={pastGuess.cellStyles.height}>{pastGuess.height}</td>
                                    <td className={pastGuess.cellStyles.country}>{pastGuess.country}</td>
                                    <td className={pastGuess.cellStyles.position}>{pastGuess.position}</td>
                                    <td className={pastGuess.cellStyles.conference}>{pastGuess.conference}</td>
                                    <td className={pastGuess.cellStyles.division}>{pastGuess.division}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {showPopup && winner && (
                <div className="popup">
                    <div className="popup-content">
                        <span className="close-button" onClick={handlePopupClose}>×</span>
                        <h2>Congratulations!</h2>
                        <p>You guessed the player correctly!</p>
                        <img src={winner.headshot} alt={winner.name} className="headshot" />
                    </div>
                </div>
            )}
        </div>
    );
};

export default Random;
