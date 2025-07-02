const express = require('express');
const axios = require('axios');
const Joi = require('joi');
const router = express.Router();

// Validation schemas
const portfolioAnalysisSchema = Joi.object({
  portfolio: Joi.array().items(
    Joi.object({
      symbol: Joi.string().required().min(1).max(10),
      value: Joi.number().positive().required()
    })
  ).min(1).required()
});

const recommendationsSchema = Joi.object({
  portfolio: Joi.array().items(
    Joi.object({
      symbol: Joi.string().required(),
      value: Joi.number().positive().required()
    })
  ).min(1).required(),
  risk_tolerance: Joi.string().valid('conservative', 'moderate', 'aggressive').default('moderate')
});

// Analyze portfolio and assess risk
router.post('/analyze', async (req, res) => {
  try {
    const { error, value } = portfolioAnalysisSchema.validate(req.body);
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }

    const { portfolio } = value;

    // Send to AI service
    const response = await axios.post(`${process.env.AI_SERVICE_URL}/portfolio/analyze`, {
      portfolio
    });

    res.json(response.data);

  } catch (error) {
    console.error('Error analyzing portfolio:', error.message);
    if (error.response) {
      res.status(error.response.status).json(error.response.data);
    } else {
      res.status(500).json({ error: 'Failed to analyze portfolio' });
    }
  }
});

// Get portfolio recommendations
router.post('/recommendations', async (req, res) => {
  try {
    const { error, value } = recommendationsSchema.validate(req.body);
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }

    const { portfolio, risk_tolerance } = value;

    // Send to AI service
    const response = await axios.post(`${process.env.AI_SERVICE_URL}/portfolio/recommendations`, {
      portfolio,
      risk_tolerance
    });

    res.json(response.data);

  } catch (error) {
    console.error('Error getting recommendations:', error.message);
    if (error.response) {
      res.status(error.response.status).json(error.response.data);
    } else {
      res.status(500).json({ error: 'Failed to get recommendations' });
    }
  }
});

// Get stock information
router.get('/stock-info/:symbol', async (req, res) => {
  try {
    const { symbol } = req.params;

    if (!symbol) {
      return res.status(400).json({ error: 'Stock symbol is required' });
    }

    // Send to AI service
    const response = await axios.get(`${process.env.AI_SERVICE_URL}/portfolio/stock-info/${symbol.toUpperCase()}`);

    res.json(response.data);

  } catch (error) {
    console.error('Error getting stock info:', error.message);
    if (error.response) {
      res.status(error.response.status).json(error.response.data);
    } else {
      res.status(500).json({ error: 'Failed to get stock info' });
    }
  }
});

// Get stock risk metrics
router.get('/risk-metrics/:symbol', async (req, res) => {
  try {
    const { symbol } = req.params;

    if (!symbol) {
      return res.status(400).json({ error: 'Stock symbol is required' });
    }

    // Send to AI service
    const response = await axios.get(`${process.env.AI_SERVICE_URL}/portfolio/risk-metrics/${symbol.toUpperCase()}`);

    res.json(response.data);

  } catch (error) {
    console.error('Error getting risk metrics:', error.message);
    if (error.response) {
      res.status(error.response.status).json(error.response.data);
    } else {
      res.status(500).json({ error: 'Failed to get risk metrics' });
    }
  }
});

// Get available stocks for portfolio building
router.get('/available-stocks', async (req, res) => {
  try {
    // Popular stocks for portfolio building
    const popularStocks = [
      { symbol: 'AAPL', name: 'Apple Inc.', sector: 'Technology' },
      { symbol: 'MSFT', name: 'Microsoft Corporation', sector: 'Technology' },
      { symbol: 'GOOGL', name: 'Alphabet Inc.', sector: 'Technology' },
      { symbol: 'AMZN', name: 'Amazon.com Inc.', sector: 'Consumer Cyclical' },
      { symbol: 'TSLA', name: 'Tesla Inc.', sector: 'Consumer Cyclical' },
      { symbol: 'META', name: 'Meta Platforms Inc.', sector: 'Communication Services' },
      { symbol: 'NVDA', name: 'NVIDIA Corporation', sector: 'Technology' },
      { symbol: 'JPM', name: 'JPMorgan Chase & Co.', sector: 'Financial Services' },
      { symbol: 'JNJ', name: 'Johnson & Johnson', sector: 'Healthcare' },
      { symbol: 'V', name: 'Visa Inc.', sector: 'Financial Services' },
      { symbol: 'PG', name: 'Procter & Gamble Co.', sector: 'Consumer Defensive' },
      { symbol: 'HD', name: 'Home Depot Inc.', sector: 'Consumer Cyclical' },
      { symbol: 'MA', name: 'Mastercard Inc.', sector: 'Financial Services' },
      { symbol: 'UNH', name: 'UnitedHealth Group Inc.', sector: 'Healthcare' },
      { symbol: 'DIS', name: 'Walt Disney Co.', sector: 'Communication Services' },
      { symbol: 'PYPL', name: 'PayPal Holdings Inc.', sector: 'Financial Services' },
      { symbol: 'ADBE', name: 'Adobe Inc.', sector: 'Technology' },
      { symbol: 'CRM', name: 'Salesforce Inc.', sector: 'Technology' },
      { symbol: 'NFLX', name: 'Netflix Inc.', sector: 'Communication Services' },
      { symbol: 'NKE', name: 'Nike Inc.', sector: 'Consumer Cyclical' },
      { symbol: 'KO', name: 'Coca-Cola Co.', sector: 'Consumer Defensive' },
      { symbol: 'PEP', name: 'PepsiCo Inc.', sector: 'Consumer Defensive' },
      { symbol: 'WMT', name: 'Walmart Inc.', sector: 'Consumer Defensive' },
      { symbol: 'COST', name: 'Costco Wholesale Corp.', sector: 'Consumer Defensive' },
      { symbol: 'BA', name: 'Boeing Co.', sector: 'Industrials' },
      { symbol: 'CAT', name: 'Caterpillar Inc.', sector: 'Industrials' },
      { symbol: 'XOM', name: 'Exxon Mobil Corp.', sector: 'Energy' },
      { symbol: 'CVX', name: 'Chevron Corp.', sector: 'Energy' }
    ];

    res.json(popularStocks);

  } catch (error) {
    console.error('Error getting available stocks:', error.message);
    res.status(500).json({ error: 'Failed to get available stocks' });
  }
});

module.exports = router; 