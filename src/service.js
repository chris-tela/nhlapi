const getData = async (link) => {
  try {
    const response = await fetch(link);
    if (!response.ok) {
      throw new Error('Network response unsuccessful');
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching player data:', error);
    throw error;
  }
};

export const getPlayerData = async () => {
  return getData('http://127.0.0.1:8000/data');
}
export const getRandomPlayer = async () => {
  return getData('http://127.0.0.1:8000/random');
}
export const getAllPlayers = async () => {
  return getData('http://127.0.0.1:8000/all_names')
}

