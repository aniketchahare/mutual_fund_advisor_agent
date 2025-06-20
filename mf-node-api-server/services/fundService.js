const Fund = require('../models/Fund');

function parsePercent(val) {
  if (typeof val === 'string') {
    const n = parseInt(val.replace('%', '').trim(), 10);
    return isNaN(n) ? undefined : n;
  }
  if (typeof val === 'number') return Math.trunc(val);
  return undefined;
}

const fundService = {
  async getAllFunds() {
    return await Fund.find({ is_active: true });
  },

  async getFundById(fundId) {
    return await Fund.findById(fundId);
  },

  async createFund(fundData) {
    const fund = new Fund({
      name: fundData.name,
      risk_level: fundData.risk_level,
      fund_type: fundData.fund_type,
      category: fundData.category,
      min_sip_amount: fundData.min_sip_amount,
      nav: fundData.nav,
      fund_size: fundData.fund_size,
      returns: fundData.returns,
      is_active: fundData.is_active !== undefined ? fundData.is_active : true
    });
    return await fund.save();
  },

  async updateFund(fundId, updateData) {
    return await Fund.findByIdAndUpdate(
      fundId,
      {
        $set: {
          name: updateData.name,
          risk_level: updateData.risk_level,
          fund_type: updateData.fund_type,
          category: updateData.category,
          min_sip_amount: updateData.min_sip_amount,
          nav: updateData.nav,
          fund_size: updateData.fund_size,
          returns: updateData.returns,
          is_active: updateData.is_active
        }
      },
      { new: true, runValidators: true }
    );
  },

  async deleteFund(fundId) {
    return await Fund.findByIdAndUpdate(
      fundId,
      { is_active: false },
      { new: true }
    );
  },

  async updateNav(fundId, newNav) {
    return await Fund.findByIdAndUpdate(
      fundId,
      { nav: newNav },
      { new: true, runValidators: true }
    );
  },

  async bulkInsertFunds(fundsData) {
    // Map Excel columns to Fund model fields (only new format supported)
    const mappedFunds = fundsData.map(row => ({
      name: row['Fund Name'],
      risk_level: row['Risk Level'],
      fund_type: row['Fund Type'],
      category: row['Category'],
      min_sip_amount: parseFloat(row['Min SIP Amount']),
      nav: parseFloat(row['Nav']),
      fund_size: parseFloat(row['Fund Size']),
      returns: {
        '1W': parsePercent(row['1W']),
        '1M': parsePercent(row['1M']),
        '3M': parsePercent(row['3M']),
        '6M': parsePercent(row['6M']),
        'YTD': parsePercent(row['YTD']),
        '1Y': parsePercent(row['1Y']),
        '2Y': parsePercent(row['2Y']),
        '3Y': parsePercent(row['3Y']),
        '5Y': parsePercent(row['5Y']),
        '10Y': parsePercent(row['10Y'])
      },
      is_active: true
    }));
    // Insert all funds
    const result = await Fund.insertMany(mappedFunds, { ordered: false });
    return result;
  }
};

module.exports = fundService;