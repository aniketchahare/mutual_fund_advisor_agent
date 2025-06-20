const mongoose = require('mongoose');

const transactionSchema = new mongoose.Schema({
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  fund: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Fund',
    required: true
  },
  type: {
    type: String,
    required: true,
    enum: ['SIP', 'LUMPSUM']
  },
  amount: {
    type: Number,
    required: true,
    min: 0
  },
  units: {
    type: Number,
    required: true,
    min: 0
  },
  nav_at_purchase: {
    type: Number,
    required: true,
    min: 0
  },
  frequency: {
    type: String,
    enum: ['DAILY', 'WEEKLY', 'MONTHLY', 'QUARTERLY'],
    required: function() {
      return this.type === 'SIP';
    }
  },
  deduction_day: {
    type: Number,
    min: 1,
    max: 31,
    required: function() {
      return this.type === 'SIP' && this.frequency === 'MONTHLY';
    }
  },
  start_date: {
    type: Date,
    required: true
  },
  end_date: {
    type: Date,
    required: function() {
      return this.type === 'SIP';
    }
  },
  status: {
    type: String,
    enum: ['ACTIVE', 'PAUSED', 'CANCELLED', 'COMPLETED'],
    default: 'ACTIVE'
  },
  last_deduction_date: {
    type: Date
  },
  next_deduction_date: {
    type: Date
  }
}, {
  timestamps: true
});

module.exports = mongoose.model('Transaction', transactionSchema); 