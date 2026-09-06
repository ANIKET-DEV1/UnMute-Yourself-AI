import { useEffect, useState } from 'react';
import './App.css';

function App() {
  const [flowers, setFlowers] = useState([]);

  // Upar se girne wale flowers ka logic
  useEffect(() => {
    const newFlowers = Array.from({ length: 35 }).map((_, i) => ({
      id: i,
      left: Math.random() * 100, // Random horizontal position
      delay: Math.random() * 5,  // Random start time
      duration: Math.random() * 3 + 4 // Girne ki speed (4s to 7s)
    }));
    setFlowers(newFlowers);
  }, []);

  return (
    <div className="container">
      {/* Falling Flowers */}
      {flowers.map((flower) => (
        <span
          key={flower.id}
          className="flower"
          style={{
            left: `${flower.left}vw`,
            animationDelay: `${flower.delay}s`,
            animationDuration: `${flower.duration}s`
          }}
        >
          🌸
        </span>
      ))}
      
      {/* Main Content Box */}
      <div className="content">
        <h1 className="name-title">PRIYA</h1>
        <div className="shayari">
          <p>Ek bewafa ke zakhmon par marham lagane hum gaye...</p>
          <br/>
          <p>Marham ki qasam, marham na mila,</p>
          <p>Marham ki jagah, mar hum gaye 💔</p>
        </div>
      </div>
    </div>
  );
}

export default App;