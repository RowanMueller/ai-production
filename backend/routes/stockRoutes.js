const express = require('express');
const axios = require('axios');
const Joi = require('joi');
const router = express.Router();

// Validation schemas
const predictSchema = Joi.object({
  symbol: Joi.string().required().min(1).max(10),
  days: Joi.number().integer().min(1).max(30).default(7),
  model: Joi.string().valid('lstm', 'linear', 'ensemble').default('lstm')
});

const historySchema = Joi.object({
  symbol: Joi.string().required().min(1).max(10),
  period: Joi.string().valid('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max').default('1y')
});

// Get available stocks
router.get('/available', async (req, res) => {
  try {
    const response = await axios.get(`${process.env.AI_SERVICE_URL}/stocks/available`);
    res.json(response.data);
  } catch (error) {
    console.error('Error fetching available stocks:', error.message);
    res.status(500).json({ error: 'Failed to fetch available stocks' });
  }
});

// Get stock prediction
router.post('/predict', async (req, res) => {
  try {
    const { error, value } = predictSchema.validate(req.body);
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }

    const response = await axios.post(`${process.env.AI_SERVICE_URL}/predict`, value);
    res.json(response.data);
  } catch (error) {
    console.error('Error predicting stock:', error.message);
    res.status(500).json({ error: 'Failed to predict stock price' });
  }
});

// Get historical data
router.get('/history/:symbol', async (req, res) => {
  try {
    const { error, value } = historySchema.validate({
      symbol: req.params.symbol,
      period: req.query.period
    });
    
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }

    const response = await axios.get(`${process.env.AI_SERVICE_URL}/history`, { params: value });
    res.json(response.data);
  } catch (error) {
    console.error('Error fetching historical data:', error.message);
    res.status(500).json({ error: 'Failed to fetch historical data' });
  }
});

// Get stock analysis
router.get('/analysis/:symbol', async (req, res) => {
  try {
    const response = await axios.get(`${process.env.AI_SERVICE_URL}/analysis/${req.params.symbol}`);
    res.json(response.data);
  } catch (error) {
    console.error('Error fetching stock analysis:', error.message);
    res.status(500).json({ error: 'Failed to fetch stock analysis' });
  }
});

// Get market sentiment
router.get('/sentiment/:symbol', async (req, res) => {
  try {
    const response = await axios.get(`${process.env.AI_SERVICE_URL}/sentiment/${req.params.symbol}`);
    res.json(response.data);
  } catch (error) {
    console.error('Error fetching market sentiment:', error.message);
    res.status(500).json({ error: 'Failed to fetch market sentiment' });
  }
});

// Get portfolio recommendations
router.post('/recommendations', async (req, res) => {
  try {
    const response = await axios.post(`${process.env.AI_SERVICE_URL}/recommendations`, req.body);
    res.json(response.data);
  } catch (error) {
    console.error('Error fetching recommendations:', error.message);
    res.status(500).json({ error: 'Failed to fetch recommendations' });
  }
});

module.exports = router; 