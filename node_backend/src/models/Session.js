const { DataTypes } = require('sequelize');
const sequelize = require('../config/db');
const User = require('./User');

const Session = sequelize.define('Session', {
  id: {
    type: DataTypes.STRING,
    primaryKey: true,
  },
  userId: {
    type: DataTypes.INTEGER,
    allowNull: false,
    references: {
      model: User,
      key: 'id',
    },
  },
  mode: {
    type: DataTypes.STRING,
    allowNull: false,
    defaultValue: 'GROUP_DISCUSSION',
  },
  topic: {
    type: DataTypes.STRING,
    allowNull: true,
  },
  durationMins: {
    type: DataTypes.INTEGER,
    defaultValue: 20,
  },
  status: {
    type: DataTypes.STRING,
    defaultValue: 'IN_PROGRESS', // IN_PROGRESS, COMPLETED, CANCELLED
  },
  transcript: {
    type: DataTypes.TEXT('long'),
    allowNull: true,
  },
  report: {
    type: DataTypes.TEXT('long'),
    allowNull: true,
  },
  startedAt: {
    type: DataTypes.DATE,
    defaultValue: DataTypes.NOW,
  },
  completedAt: {
    type: DataTypes.DATE,
    allowNull: true,
  },
}, {
  tableName: 'sessions',
  timestamps: true,
});

User.hasMany(Session, { foreignKey: 'userId' });
Session.belongsTo(User, { foreignKey: 'userId' });

module.exports = Session;
