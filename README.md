**NHL Player Guessing Game**

This project is a web-interactive guessing game in which a user tries to guess the NHL player based on hints such as the player's points, nationality, team, etc. 

**Contents of this file:**
- Features
- Technologies Used
- How it works
- Preview

**Features**
- Player search box: Program suggests player names as user types.
- Player database: Entire NHL player database is available and up-to-date
- Dynamic feedback: Each guess is logged in a table which provides visual feedback; green if correct, yellow if close, red if incorrect

**Technologies Used**
- Python: Used for backend processing, data handling, and integrating with APIs
- FastAPI: Used for building APIs with Python
- PostgreSQL: Used for storing player data
- React: For building user interface
- HTML/CSS: Styling the website
- JavaScript: Main programming language used for front-end logic and interactivity

**How it Works**
One random NHL player is picked out from the database to be the "mystery player", the user's goal is to guess the player within 7 guesses. You are given information based on every guess, such as if your guessed player has played on the same team, if they are the same age, etc. 

**Preview:**

![Example](https://github.com/chris-tela/nhlapi/blob/main/Screenshot%202025-01-11%20181418.png)

