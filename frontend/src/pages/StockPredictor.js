import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  Search, 
  Calendar, 
  BarChart3,
  Target,
  Activity,
  ArrowUp,
  ArrowDown,
  Loader2
} from 'lucide-react';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import toast from 'react-hot-toast';
import apiClient from '../api';

const StockPredictor = () => {
  const [selectedStock, setSelectedStock] = useState('');
  const [predictionDays, setPredictionDays] = useState(7);
  const [modelType, setModelType] = useState('lstm');
  const [isLoading, setIsLoading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [availableStocks, setAvailableStocks] = useState([]);
  const [stockAnalysis, setStockAnalysis] = useState(null);

  const popularStocks = [
    'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
    'ADBE', 'CRM', 'ORCL', 'INTC', 'AMD', 'IBM', 'CSCO', 'QCOM'
  ];

  useEffect(() => {
    const fetchAvailableStocks = async () => {
      try {
        const response = await apiClient.get('/stocks/available');
        setAvailableStocks(response.data.stocks);
      } catch (error) {
        console.error("Failed to fetch available stocks", error);
        toast.error('Could not load available stocks.');
      }
    };
    fetchAvailableStocks();
  }, []);

  const handlePrediction = async () => {
    if (!selectedStock) {
      toast.error('Please select a stock symbol');
      return;
    }

    setIsLoading(true);
    setPrediction(null);
    try {
      const response = await apiClient.post('/stocks/predict', {
        symbol: selectedStock,
        days: predictionDays,
        model: modelType,
      });
      // The API returns predictions as a list of numbers, we need to format it for the chart
      const formattedPredictions = response.data.dates.map((date, index) => ({
        date: new Date(date).toLocaleDateString(),
        price: response.data.predictions[index],
      }));
      setPrediction({ ...response.data, predictions: formattedPredictions });
      toast.success('Prediction completed successfully!');
    } catch (error) {
      console.error("Prediction failed", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnalysis = async () => {
    if (!selectedStock) {
      toast.error('Please select a stock symbol');
      return;
    }

    setIsAnalyzing(true);
    setStockAnalysis(null);
    try {
      const response = await apiClient.get(`/stocks/analysis/${selectedStock}`);
      setStockAnalysis(response.data);
      toast.success('Analysis completed!');
    } catch (error) {
      console.error("Analysis failed", error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getPriceChangeColor = (change) => {
    return change >= 0 ? 'text-green-600' : 'text-red-600';
  };

  const getPriceChangeIcon = (change) => {
    return change >= 0 ? <ArrowUp className="h-4 w-4" /> : <ArrowDown className="h-4 w-4" />;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Stock Price Predictor</h1>
        <p className="mt-2 text-gray-600">
          Get AI-powered stock price predictions using advanced machine learning models.
        </p>
      </div>

      {/* Prediction Form */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card"
      >
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Generate Prediction</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Stock Symbol
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <select
                value={selectedStock}
                onChange={(e) => setSelectedStock(e.target.value)}
                className="input pl-10"
              >
                <option value="">Select a stock</option>
                {availableStocks.map((stock) => (
                  <option key={stock} value={stock}>{stock}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Prediction Days
            </label>
            <select
              value={predictionDays}
              onChange={(e) => setPredictionDays(Number(e.target.value))}
              className="input"
            >
              <option value={7}>7 days</option>
              <option value={14}>14 days</option>
              <option value={30}>30 days</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Model Type
            </label>
            <select
              value={modelType}
              onChange={(e) => setModelType(e.target.value)}
              className="input"
            >
              <option value="lstm">LSTM</option>
              <option value="linear">Linear Regression</option>
              <option value="ensemble">Ensemble</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={handlePrediction}
              disabled={isLoading || !selectedStock}
              className="btn-primary w-full flex items-center justify-center"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <TrendingUp className="h-4 w-4 mr-2" />
              )}
              {isLoading ? 'Predicting...' : 'Predict'}
            </button>
          </div>
        </div>
      </motion.div>

      {/* Prediction Results */}
      {prediction && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card"
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">
              Prediction Results for {prediction.symbol}
            </h2>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-500">Confidence:</span>
              <span className="text-sm font-medium text-green-600">
                {(prediction.confidence * 100).toFixed(1)}%
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Chart */}
            <div>
              <h3 className="text-md font-medium text-gray-900 mb-3">Price Forecast</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={prediction.predictions}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis domain={['auto', 'auto']} />
                    <Tooltip />
                    <Line 
                      type="monotone" 
                      dataKey="price" 
                      stroke="#3b82f6" 
                      strokeWidth={2}
                      dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Prediction Details */}
            <div>
              <h3 className="text-md font-medium text-gray-900 mb-3">Prediction Details</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm text-gray-600">Current Price</span>
                  <span className="text-sm font-medium text-gray-900">
                    ${prediction.current_price.toFixed(2)}
                  </span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm text-gray-600">Model Used</span>
                  <span className="text-sm font-medium text-gray-900 uppercase">
                    {prediction.model_type}
                  </span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm text-gray-600">Prediction Period</span>
                  <span className="text-sm font-medium text-gray-900">
                    {prediction.predictions.length} days
                  </span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm text-gray-600">Expected Range</span>
                  <span className="text-sm font-medium text-gray-900">
                    ${Math.min(...prediction.predictions.map(p => p.price)).toFixed(2)} - 
                    ${Math.max(...prediction.predictions.map(p => p.price)).toFixed(2)}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Stock Analysis */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card"
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Stock Analysis</h2>
          <button
            onClick={handleAnalysis}
            disabled={isAnalyzing || !selectedStock}
            className="btn-secondary flex items-center"
          >
            {isAnalyzing ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <BarChart3 className="h-4 w-4 mr-2" />}
            {isAnalyzing ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>

        {stockAnalysis ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Price Changes */}
            <div>
              <h3 className="text-md font-medium text-gray-900 mb-3">Price Changes</h3>
              <div className="space-y-3">
                {Object.entries(stockAnalysis.price_changes).map(([period, change]) => (
                  <div key={period} className="flex justify-between items-center">
                    <span className="text-sm text-gray-600 capitalize">{period}</span>
                    <div className={`flex items-center ${getPriceChangeColor(change)}`}>
                      {getPriceChangeIcon(change)}
                      <span className="ml-1 text-sm font-medium">
                        {change >= 0 ? '+' : ''}{change.toFixed(2)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Technical Indicators */}
            <div>
              <h3 className="text-md font-medium text-gray-900 mb-3">Technical Indicators</h3>
              <div className="space-y-3">
                {Object.entries(stockAnalysis.technical_indicators).map(([key, value]) => (
                  <div key={key} className="flex justify-between items-center">
                    <span className="text-sm text-gray-600 uppercase">{key.replace('_', ' ')}</span>
                    <span className="text-sm font-medium text-gray-900">
                      {typeof value === 'number' ? value.toFixed(2) : value}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Sentiment & Recommendation */}
            <div>
              <h3 className="text-md font-medium text-gray-900 mb-3">Analysis</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Current Price</span>
                  <span className="text-sm font-medium text-gray-900">
                    ${stockAnalysis.current_price.toFixed(2)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Sentiment</span>
                  <span className={`badge ${
                    stockAnalysis.sentiment?.sentiment_level === 'bullish' ? 'badge-success' : 
                    stockAnalysis.sentiment?.sentiment_level === 'bearish' ? 'badge-danger' : 'badge-warning'
                  }`}>
                    {stockAnalysis.sentiment?.sentiment_level || 'N/A'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-8">
            <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">Select a stock and click "Analyze" to get detailed analysis</p>
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default StockPredictor; 