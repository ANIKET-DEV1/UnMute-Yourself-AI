const express = require('express');
const router = express.Router();
const { saveInternalReport } = require('../controllers/sessionController');

// POST /api/internal/sessions/:id/report
router.post('/sessions/:id/report', saveInternalReport);

module.exports = router;
