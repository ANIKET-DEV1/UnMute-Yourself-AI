const express = require('express');
const cors = require('cors');
require('dotenv').config();

const sequelize = require('./src/config/db');
const authRoutes = require('./src/routes/authRoutes');

const app = express();

app.use(cors());
app.use(express.json());

// Routes
app.use('/api/auth', authRoutes);

// DB Sync + Server Start
const PORT = process.env.PORT || 5000;

sequelize.sync({ alter: true })
  .then(() => {
    console.log('MySQL connected & tables synced');
    app.listen(PORT, () => console.log(`Node server running on port ${PORT}`));
  })
  .catch((err) => console.error('DB connection failed:', err));