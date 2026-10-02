const express = require('express');
const router = express.Router();
const {
  createSession,
  getSessionById,
  getUserSessions,
  saveInternalReport,
} = require('../controllers/sessionController');
const { protect } = require('../middleware/authMiddleware');

// Session Routes
router.post('/create', protect, createSession);
router.get('/my-sessions', protect, getUserSessions);
router.get('/user/:userId', protect, getUserSessions);
router.get('/:id', getSessionById);
router.post('/:id/report', saveInternalReport);

module.exports = router;
