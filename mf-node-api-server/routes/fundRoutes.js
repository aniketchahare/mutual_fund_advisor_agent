const express = require('express');
const router = express.Router();
const fundController = require('../controllers/fundController');
const multer = require('multer');
const upload = multer({ dest: 'uploads/' });

// Get all funds
router.get('/', fundController.getAllFunds);

// Get fund by ID
router.get('/:id', fundController.getFundById);

// Create new fund
router.post('/', fundController.createFund);

// Bulk upload funds via Excel
router.post('/upload', upload.single('file'), fundController.uploadFundsFromExcel);

// Update fund
router.put('/:id', fundController.updateFund);

// Delete fund
router.delete('/:id', fundController.deleteFund);

// Update fund NAV
router.patch('/:id/nav', fundController.updateNav);

module.exports = router; 