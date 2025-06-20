const mongoose = require('mongoose');

const fundSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    trim: true
  },
  risk_level: {
    type: String,
    trim: true
  },
  fund_type: {
    type: String,
    trim: true
  },
  category: {
    type: String,
    required: true,
    trim: true
  },
  min_sip_amount: {
    type: Number
  },
  nav: {
    type: Number
  },
  fund_size: {
    type: Number
  },
  returns: {
    '1W': { type: Number },
    '1M': { type: Number },
    '3M': { type: Number },
    '6M': { type: Number },
    'YTD': { type: Number },
    '1Y': { type: Number },
    '2Y': { type: Number },
    '3Y': { type: Number },
    '5Y': { type: Number },
    '10Y': { type: Number }
  },

  is_active: {
    type: Boolean,
    default: true
  }
}, {
  timestamps: true
});

module.exports = mongoose.model('Fund', fundSchema); 