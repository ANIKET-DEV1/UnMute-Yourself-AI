const express = require('express');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

const sequelize = require('./src/config/db');
const authRoutes = require('./src/routes/authRoutes');
const sessionRoutes = require('./src/routes/sessionRoutes');
const internalRoutes = require('./src/routes/internalRoutes');

const app = express();

// Enable CORS for all origins
app.use(cors({
  origin: '*',
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
}));

app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Serve frontend static files
const frontendPath = path.join(__dirname, '../frontend');
app.use(express.static(frontendPath));
app.use(express.static(path.join(frontendPath, 'html')));
app.use('/html', express.static(path.join(frontendPath, 'html')));
app.use('/js', express.static(path.join(frontendPath, 'js')));

// API Routes (Node.js handles all Auth, Sessions, and DB persistence)
app.use('/api/auth', authRoutes);
app.use('/api/sessions', sessionRoutes);
app.use('/api/internal', internalRoutes);

// Page Shortcuts & Direct HTML Routes served by Node.js
app.get('/login', (req, res) => res.sendFile(path.join(frontendPath, 'html', 'login.html')));
app.get('/login.html', (req, res) => res.sendFile(path.join(frontendPath, 'html', 'login.html')));

app.get('/register', (req, res) => res.sendFile(path.join(frontendPath, 'html', 'register.html')));
app.get('/register.html', (req, res) => res.sendFile(path.join(frontendPath, 'html', 'register.html')));

app.get('/dashboard', (req, res) => res.sendFile(path.join(frontendPath, 'html', 'index.html')));
app.get('/index.html', (req, res) => res.sendFile(path.join(frontendPath, 'html', 'index.html')));

app.get('/gd', (req, res) => res.sendFile(path.join(frontendPath, 'html', 'gd.html')));
app.get('/gd.html', (req, res) => res.sendFile(path.join(frontendPath, 'html', 'gd.html')));

app.get('/debate', (req, res) => res.sendFile(path.join(frontendPath, 'html', 'debate.html')));
app.get('/debate.html', (req, res) => res.sendFile(path.join(frontendPath, 'html', 'debate.html')));

app.get('/interview', (req, res) => res.sendFile(path.join(frontendPath, 'html', 'interview.html')));
app.get('/interview.html', (req, res) => res.sendFile(path.join(frontendPath, 'html', 'interview.html')));

app.get('/landing', (req, res) => res.sendFile(path.join(frontendPath, 'html', 'landing.html')));
app.get('/landing.html', (req, res) => res.sendFile(path.join(frontendPath, 'html', 'landing.html')));

// Default Root Route
app.get('/', (req, res) => {
  res.sendFile(path.join(frontendPath, 'html', 'index.html'));
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'OK', message: 'UnMute Node Backend Operational' });
});

// DB Sync + Server Start
const PORT = process.env.PORT || 5000;

sequelize.sync({ alter: true })
  .then(() => {
    console.log('✅ Database connected & tables synced');
    app.listen(PORT, () => {
      console.log(`🚀 Node server running on http://localhost:${PORT}`);
    });
  })
  .catch((err) => {
    console.error('❌ DB connection error:', err.message);
    app.listen(PORT, () => {
      console.log(`🚀 Node server running on http://localhost:${PORT} (without DB sync)`);
    });
  });