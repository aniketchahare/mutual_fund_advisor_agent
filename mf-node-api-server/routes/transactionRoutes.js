const express = require('express');
const router = express.Router();
const transactionController = require('../controllers/transactionController');
const auth = require('../middleware/auth');

// All transaction routes require authentication
router.use(auth);

// Create SIP
router.post('/sip', transactionController.createSIP);

// Create Lumpsum
router.post('/lumpsum', transactionController.createLumpsum);

// Get user portfolio
router.get('/portfolio/:userId', transactionController.getUserPortfolio);

// Get next deduction dates for all active SIPs
router.get('/deduction-dates', transactionController.getNextDeductionDates);

// Update next deduction date after successful deduction
router.patch('/:id/update-deduction-date', transactionController.updateNextDeductionDate);

// Pause SIP
router.patch('/:id/pause', transactionController.pauseSIP);

// Resume SIP
router.patch('/:id/resume', transactionController.resumeSIP);

// Cancel transaction
router.patch('/:id/cancel', transactionController.cancelTransaction);

// Get transaction details
router.get('/:id', transactionController.getTransactionDetails);

module.exports = router; 