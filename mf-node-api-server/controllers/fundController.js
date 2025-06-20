const fundService = require('../services/fundService');
const xlsx = require('xlsx');
const fs = require('fs');

const fundController = {
  async getAllFunds(req, res) {
    try {
      const funds = await fundService.getAllFunds();
      res.json(funds);
    } catch (error) {
      res.status(500).json({ message: error.message });
    }
  },

  async getFundById(req, res) {
    try {
      const fund = await fundService.getFundById(req.params.id);
      if (!fund) {
        return res.status(404).json({ message: 'Fund not found' });
      }
      res.json(fund);
    } catch (error) {
      res.status(500).json({ message: error.message });
    }
  },

  async createFund(req, res) {
    try {
      const fund = await fundService.createFund(req.body);
      res.status(201).json(fund);
    } catch (error) {
      res.status(400).json({ message: error.message });
    }
  },

  async updateFund(req, res) {
    try {
      const fund = await fundService.updateFund(req.params.id, req.body);
      if (!fund) {
        return res.status(404).json({ message: 'Fund not found' });
      }
      res.json(fund);
    } catch (error) {
      res.status(400).json({ message: error.message });
    }
  },

  async deleteFund(req, res) {
    try {
      const fund = await fundService.deleteFund(req.params.id);
      if (!fund) {
        return res.status(404).json({ message: 'Fund not found' });
      }
      res.json({ message: 'Fund deleted successfully' });
    } catch (error) {
      res.status(500).json({ message: error.message });
    }
  },

  async updateNav(req, res) {
    try {
      const { newNav } = req.body;
      const fund = await fundService.updateNav(req.params.id, newNav);
      if (!fund) {
        return res.status(404).json({ message: 'Fund not found' });
      }
      res.json(fund);
    } catch (error) {
      res.status(400).json({ message: error.message });
    }
  },

  async uploadFundsFromExcel(req, res) {
    try {
      if (!req.file) {
        return res.status(400).json({ message: 'No file uploaded' });
      }
      // Read and parse the Excel file
      const workbook = xlsx.readFile(req.file.path);
      const sheetName = workbook.SheetNames[0];
      const sheet = workbook.Sheets[sheetName];
      const data = xlsx.utils.sheet_to_json(sheet);

      // Remove the uploaded file after reading
      fs.unlinkSync(req.file.path);

      // Insert funds in bulk
      const result = await fundService.bulkInsertFunds(data);
      res.json({ message: 'Funds uploaded successfully', inserted: result.length });
    } catch (error) {
      res.status(500).json({ message: error.message });
    }
  }
};

module.exports = fundController; 