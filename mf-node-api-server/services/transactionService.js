const Transaction = require('../models/Transaction');
const Fund = require('../models/Fund');
const User = require('../models/User');

const transactionService = {
  async createSIP(userId, fundId, amount, frequency, startDate, endDate, deductionDay) {
    const fund = await Fund.findById(fundId);
    if (!fund) throw new Error('Fund not found');
    if (amount < fund.min_investment) throw new Error('Amount below minimum investment');

    const user = await User.findById(userId);
    if (!user) throw new Error('User not found');

    // Validate deduction day for monthly SIP
    if (frequency.toUpperCase() === 'MONTHLY') {
      if (!deductionDay || deductionDay < 1 || deductionDay > 31) {
        throw new Error('Invalid deduction day. Must be between 1 and 31');
      }
    }

    const units = amount / fund.nav;
    
    // Calculate next deduction date based on frequency
    let nextDeductionDate = new Date(startDate);
    if (frequency.toUpperCase() === 'MONTHLY') {
      // Set the deduction day of the month
      nextDeductionDate.setDate(deductionDay);
      // If the deduction day has passed for the current month, set to next month
      if (nextDeductionDate < new Date()) {
        nextDeductionDate.setMonth(nextDeductionDate.getMonth() + 1);
      }
    } else if (frequency.toUpperCase() === 'WEEKLY') {
      // Set to next Monday
      const daysUntilMonday = (8 - nextDeductionDate.getDay()) % 7;
      nextDeductionDate.setDate(nextDeductionDate.getDate() + daysUntilMonday);
    } else if (frequency.toUpperCase() === 'DAILY') {
      // Set to next day
      nextDeductionDate.setDate(nextDeductionDate.getDate() + 1);
    } else if (frequency.toUpperCase() === 'QUARTERLY') {
      // Set to same day next quarter
      nextDeductionDate.setMonth(nextDeductionDate.getMonth() + 3);
    }
    
    const transaction = new Transaction({
      user: userId,
      fund: fundId,
      type: 'SIP',
      amount,
      units,
      nav_at_purchase: fund.nav,
      frequency: frequency.toUpperCase(),
      deduction_day: deductionDay,
      start_date: startDate,
      end_date: endDate,
      next_deduction_date: nextDeductionDate
    });

    const savedTransaction = await transaction.save();
    
    // Update user's portfolio
    await User.findByIdAndUpdate(
      userId,
      { $push: { portfolio: savedTransaction._id } }
    );

    return savedTransaction;
  },

  async createLumpsum(userId, fundId, amount) {
    const fund = await Fund.findById(fundId);
    if (!fund) throw new Error('Fund not found');
    if (amount < fund.min_investment) throw new Error('Amount below minimum investment');

    const user = await User.findById(userId);
    if (!user) throw new Error('User not found');

    const units = amount / fund.nav;
    
    const transaction = new Transaction({
      user: userId,
      fund: fundId,
      type: 'LUMPSUM',
      amount,
      units,
      nav_at_purchase: fund.nav,
      start_date: new Date()
    });

    const savedTransaction = await transaction.save();
    
    // Update user's portfolio
    await User.findByIdAndUpdate(
      userId,
      { $push: { portfolio: savedTransaction._id } }
    );

    return savedTransaction;
  },

  async getUserPortfolio(userId) {
    return await Transaction.find({ user: userId })
      .populate('fund')
      .sort({ createdAt: -1 });
  },

  async pauseSIP(transactionId, userId) {
    const transaction = await Transaction.findOne({ _id: transactionId, user: userId });
    if (!transaction) throw new Error('Transaction not found');
    if (transaction.type !== 'SIP') throw new Error('Only SIP transactions can be paused');

    transaction.status = 'PAUSED';
    return await transaction.save();
  },

  async resumeSIP(transactionId, userId) {
    const transaction = await Transaction.findOne({ _id: transactionId, user: userId });
    if (!transaction) throw new Error('Transaction not found');
    if (transaction.type !== 'SIP') throw new Error('Only SIP transactions can be resumed');
    if (transaction.status !== 'PAUSED') throw new Error('Transaction is not paused');

    transaction.status = 'ACTIVE';
    return await transaction.save();
  },

  async cancelTransaction(transactionId, userId) {
    const transaction = await Transaction.findOne({ _id: transactionId, user: userId });
    if (!transaction) throw new Error('Transaction not found');
    if (transaction.status === 'CANCELLED') throw new Error('Transaction is already cancelled');

    transaction.status = 'CANCELLED';
    return await transaction.save();
  },

  async getTransactionDetails(transactionId, userId) {
    const transaction = await Transaction.findOne({ _id: transactionId, user: userId })
      .populate('fund')
      .populate('user', '-password');
    
    if (!transaction) throw new Error('Transaction not found');
    return transaction;
  },

  async getNextDeductionDates(userId) {
    const activeSIPs = await Transaction.find({
      user: userId,
      type: 'SIP',
      status: 'ACTIVE'
    }).select('fund amount frequency deduction_day next_deduction_date');

    return activeSIPs.map(sip => ({
      fundId: sip.fund,
      amount: sip.amount,
      frequency: sip.frequency,
      deductionDay: sip.deduction_day,
      nextDeductionDate: sip.next_deduction_date
    }));
  },

  async updateNextDeductionDate(transactionId, userId) {
    const transaction = await Transaction.findOne({ _id: transactionId, user: userId });
    if (!transaction) throw new Error('Transaction not found');
    if (transaction.type !== 'SIP') throw new Error('Only SIP transactions have deduction dates');
    if (transaction.status !== 'ACTIVE') throw new Error('Transaction is not active');

    const nextDate = new Date(transaction.next_deduction_date);
    
    // Update last deduction date
    transaction.last_deduction_date = transaction.next_deduction_date;

    // Calculate next deduction date based on frequency
    if (transaction.frequency.toUpperCase() === 'MONTHLY') {
      nextDate.setMonth(nextDate.getMonth() + 1);
    } else if (transaction.frequency.toUpperCase() === 'WEEKLY') {
      nextDate.setDate(nextDate.getDate() + 7);
    } else if (transaction.frequency.toUpperCase() === 'DAILY') {
      nextDate.setDate(nextDate.getDate() + 1);
    } else if (transaction.frequency.toUpperCase() === 'QUARTERLY') {
      nextDate.setMonth(nextDate.getMonth() + 3);
    }

    transaction.next_deduction_date = nextDate;
    return await transaction.save();
  }
};

module.exports = transactionService; 