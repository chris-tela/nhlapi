import './App.css';
import React from 'react';
import Random from './random.js';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>NHL Player Guessing Game</h1>
      </header>
      <main>
        <Random />
      </main>
    </div>
  );
}

export default App;
