const transactionService = require('../services/transactionService');

const transactionController = {
  async createSIP(req, res) {
    try {
      const { fundId, amount, frequency, startDate, endDate, deductionDay } = req.body;
      const userId = req.user.userId;

      const transaction = await transactionService.createSIP(
        userId,
        fundId,
        amount,
        frequency,
        startDate,
        endDate,
        deductionDay
      );
      res.status(201).json(transaction);
    } catch (error) {
      res.status(400).json({ message: error.message });
    }
  },

  async createLumpsum(req, res) {
    try {
      const { fundId, amount } = req.body;
      const userId = req.user.userId;

      const transaction = await transactionService.createLumpsum(
        userId,
        fundId,
        amount
      );
      res.status(201).json(transaction);
    } catch (error) {
      res.status(400).json({ message: error.message });
    }
  },

  async getUserPortfolio(req, res) {
    try {
      const userId = req.user.userId;
      if (req.params.userId !== userId) {
        return res.status(403).json({ message: 'Not authorized to access this portfolio' });
      }
      const portfolio = await transactionService.getUserPortfolio(userId);
      res.json(portfolio);
    } catch (error) {
      res.status(500).json({ message: error.message });
    }
  },

  async pauseSIP(req, res) {
    try {
      const userId = req.user.userId;
      const transaction = await transactionService.pauseSIP(req.params.id, userId);
      if (!transaction) {
        return res.status(404).json({ message: 'Transaction not found' });
      }
      res.json(transaction);
    } catch (error) {
      res.status(400).json({ message: error.message });
    }
  },

  async resumeSIP(req, res) {
    try {
      const userId = req.user.userId;
      const transaction = await transactionService.resumeSIP(req.params.id, userId);
      if (!transaction) {
        return res.status(404).json({ message: 'Transaction not found' });
      }
      res.json(transaction);
    } catch (error) {
      res.status(400).json({ message: error.message });
    }
  },

  async cancelTransaction(req, res) {
    try {
      const userId = req.user.userId;
      const transaction = await transactionService.cancelTransaction(req.params.id, userId);
      if (!transaction) {
        return res.status(404).json({ message: 'Transaction not found' });
      }
      res.json(transaction);
    } catch (error) {
      res.status(400).json({ message: error.message });
    }
  },

  async getTransactionDetails(req, res) {
    try {
      const userId = req.user.userId;
      const transaction = await transactionService.getTransactionDetails(req.params.id, userId);
      if (!transaction) {
        return res.status(404).json({ message: 'Transaction not found' });
      }
      res.json(transaction);
    } catch (error) {
      res.status(500).json({ message: error.message });
    }
  },

  async getNextDeductionDates(req, res) {
    try {
      const userId = req.user.userId;
      const deductionDates = await transactionService.getNextDeductionDates(userId);
      res.json(deductionDates);
    } catch (error) {
      res.status(500).json({ message: error.message });
    }
  },

  async updateNextDeductionDate(req, res) {
    try {
      const userId = req.user.userId;
      const transaction = await transactionService.updateNextDeductionDate(
        req.params.id,
        userId
      );
      res.json(transaction);
    } catch (error) {
      res.status(400).json({ message: error.message });
    }
  }
};

module.exports = transactionController; 