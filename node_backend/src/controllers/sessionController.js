const Session = require('../models/Session');
const User = require('../models/User');

// POST /api/sessions/create
const createSession = async (req, res) => {
  try {
    const { mode = 'GROUP_DISCUSSION', topic = 'General Practice', durationMins = 20 } = req.body;
    const userId = req.user.id;

    const timestamp = Date.now();
    const randomSuffix = Math.random().toString(36).substring(2, 7);
    const sessionId = `sess_${timestamp}_${randomSuffix}`;

    // Map mode to WS endpoint lower
    let modePath = 'gd';
    const modeUpper = mode.toUpperCase();
    if (modeUpper.includes('DEBATE')) modePath = 'debate';
    else if (modeUpper.includes('INTERVIEW')) modePath = 'interview';

    const wsUrl = `ws://localhost:8000/ws/${modePath}/${sessionId}`;

    const session = await Session.create({
      id: sessionId,
      userId,
      mode: modeUpper,
      topic,
      durationMins: Number(durationMins) || 20,
      status: 'IN_PROGRESS',
      startedAt: new Date(),
    });

    res.status(201).json({
      message: 'Session created successfully',
      sessionId,
      sessionToken: req.headers.authorization ? req.headers.authorization.split(' ')[1] : '',
      wsUrl,
      topic,
      mode: modeUpper,
      durationMins,
      session,
    });
  } catch (err) {
    console.error('Create Session Error:', err);
    res.status(500).json({ message: 'Failed to create session', error: err.message });
  }
};

// GET /api/sessions/:id
const getSessionById = async (req, res) => {
  try {
    const { id } = req.params;
    const session = await Session.findByPk(id, {
      include: [{ model: User, attributes: ['id', 'name', 'email'] }],
    });

    if (!session) {
      return res.status(404).json({ message: 'Session not found' });
    }

    // Format parsed JSON output if stored as JSON string
    const sessionData = session.toJSON();
    try {
      if (sessionData.report && typeof sessionData.report === 'string') {
        sessionData.report = JSON.parse(sessionData.report);
      }
      if (sessionData.transcript && typeof sessionData.transcript === 'string') {
        sessionData.transcript = JSON.parse(sessionData.transcript);
      }
    } catch (e) {
      // keep raw string if parse fails
    }

    res.status(200).json({ session: sessionData });
  } catch (err) {
    console.error('Get Session Error:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
};

// GET /api/sessions/user/:userId or GET /api/sessions/my-sessions
const getUserSessions = async (req, res) => {
  try {
    const userId = req.params.userId || req.user?.id;
    if (!userId) {
      return res.status(400).json({ message: 'User ID required' });
    }

    const sessions = await Session.findAll({
      where: { userId },
      order: [['createdAt', 'DESC']],
    });

    const parsedSessions = sessions.map((s) => {
      const item = s.toJSON();
      try {
        if (item.report && typeof item.report === 'string') {
          item.report = JSON.parse(item.report);
        }
      } catch (e) {}
      return item;
    });

    res.status(200).json({ sessions: parsedSessions });
  } catch (err) {
    console.error('Get User Sessions Error:', err);
    res.status(500).json({ message: 'Internal server error' });
  }
};

// POST /api/internal/sessions/:id/report OR POST /api/sessions/:id/report
const saveInternalReport = async (req, res) => {
  try {
    const { id } = req.params;
    const { report, transcript, status = 'COMPLETED' } = req.body;

    let session = await Session.findByPk(id);

    const reportStr = typeof report === 'object' ? JSON.stringify(report) : report;
    const transcriptStr = typeof transcript === 'object' ? JSON.stringify(transcript) : transcript;

    if (!session) {
      // If session does not exist yet (e.g. guest session created directly), create record
      session = await Session.create({
        id,
        userId: req.user?.id || 1, // default or fallback user
        mode: 'GENERAL',
        topic: 'Practice Session',
        durationMins: 20,
        status,
        report: reportStr,
        transcript: transcriptStr,
        completedAt: new Date(),
      });
    } else {
      session.status = status;
      if (reportStr) session.report = reportStr;
      if (transcriptStr) session.transcript = transcriptStr;
      session.completedAt = new Date();
      await session.save();
    }

    res.status(200).json({
      status: 'SAVED',
      message: 'Evaluation report saved successfully',
      sessionId: session.id,
    });
  } catch (err) {
    console.error('Save Report Error:', err);
    res.status(500).json({ message: 'Failed to save session report', error: err.message });
  }
};

module.exports = {
  createSession,
  getSessionById,
  getUserSessions,
  saveInternalReport,
};
