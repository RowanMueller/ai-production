from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
import logging
import asyncio

# Import our modules
from services.stock_predictor import StockPredictor
from services.enhanced_chatbot import EnhancedChatbot
from services.portfolio_analyzer import PortfolioAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize services
stock_predictor = StockPredictor()
enhanced_chatbot = EnhancedChatbot(stock_predictor=stock_predictor, data_dir="data")
portfolio_analyzer = PortfolioAnalyzer(data_dir="data")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'AI Services',
        'version': '1.0.0'
    })

# Stock Prediction Routes
@app.route('/stocks/available', methods=['GET'])
def get_available_stocks():
    """Get list of available stocks"""
    try:
        stocks = stock_predictor.get_available_stocks()
        return jsonify(stocks)
    except Exception as e:
        logger.error(f"Error getting available stocks: {str(e)}")
        return jsonify({'error': 'Failed to get available stocks'}), 500

@app.route('/predict', methods=['POST'])
def predict_stock():
    """Predict stock prices"""
    try:
        data = request.get_json()
        symbol = data.get('symbol')
        days = data.get('days', 7)
        model = data.get('model', 'lstm')
        
        if not symbol:
            return jsonify({'error': 'Symbol is required'}), 400
        
        prediction = stock_predictor.predict(symbol, days, model)
        return jsonify(prediction)
    except Exception as e:
        logger.error(f"Error predicting stock: {str(e)}")
        return jsonify({'error': 'Failed to predict stock'}), 500

@app.route('/history', methods=['GET'])
def get_history():
    """Get historical stock data"""
    try:
        symbol = request.args.get('symbol')
        period = request.args.get('period', '1y')
        
        if not symbol:
            return jsonify({'error': 'Symbol is required'}), 400
        
        history = stock_predictor.get_history(symbol, period)
        return jsonify(history)
    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        return jsonify({'error': 'Failed to get historical data'}), 500

@app.route('/analysis/<symbol>', methods=['GET'])
def analyze_stock(symbol):
    """Get comprehensive stock analysis"""
    try:
        analysis = stock_predictor.analyze_stock(symbol)
        return jsonify(analysis)
    except Exception as e:
        logger.error(f"Error analyzing stock: {str(e)}")
        return jsonify({'error': 'Failed to analyze stock'}), 500

@app.route('/sentiment/<symbol>', methods=['GET'])
def get_sentiment(symbol):
    """Get market sentiment for stock"""
    try:
        sentiment = stock_predictor.get_sentiment(symbol)
        return jsonify(sentiment)
    except Exception as e:
        logger.error(f"Error getting sentiment: {str(e)}")
        return jsonify({'error': 'Failed to get sentiment'}), 500

@app.route('/recommendations', methods=['POST'])
def get_recommendations():
    """Get portfolio recommendations"""
    try:
        data = request.get_json()
        recommendations = stock_predictor.get_recommendations(data)
        return jsonify(recommendations)
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        return jsonify({'error': 'Failed to get recommendations'}), 500

# Chatbot Routes
@app.route('/chat', methods=['POST'])
def chat():
    """Process chat message with enhanced chatbot"""
    try:
        data = request.get_json()
        message = data.get('message')
        session_id = data.get('sessionId')
        context = data.get('context', {})
        history = data.get('history', [])
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Run async process_message in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(enhanced_chatbot.process_message(message, session_id, context, history))
        finally:
            loop.close()
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        return jsonify({'error': 'Failed to process message'}), 500

@app.route('/chat/suggestions', methods=['GET'])
def get_suggestions():
    """Get chat suggestions from enhanced chatbot"""
    try:
        session_id = request.args.get('sessionId')
        context = request.args.get('context', {})
        
        suggestions = enhanced_chatbot.get_suggestions(session_id, context)
        return jsonify(suggestions)
    except Exception as e:
        logger.error(f"Error getting suggestions: {str(e)}")
        return jsonify({'error': 'Failed to get suggestions'}), 500

# Portfolio Analysis Routes (replacing Task Prioritizer)
@app.route('/portfolio/analyze', methods=['POST'])
def analyze_portfolio():
    """Analyze portfolio and assess risk"""
    try:
        data = request.get_json()
        portfolio_data = data.get('portfolio', [])
        
        if not portfolio_data:
            return jsonify({'error': 'Portfolio data is required'}), 400
        
        # Validate portfolio data structure
        for item in portfolio_data:
            if 'symbol' not in item or 'value' not in item:
                return jsonify({'error': 'Each portfolio item must have symbol and value'}), 400
        
        analysis = portfolio_analyzer.get_portfolio_analysis(portfolio_data)
        return jsonify(analysis)
        
    except Exception as e:
        logger.error(f"Error analyzing portfolio: {str(e)}")
        return jsonify({'error': 'Failed to analyze portfolio'}), 500

@app.route('/portfolio/recommendations', methods=['POST'])
def get_portfolio_recommendations():
    """Get stock recommendations for portfolio improvement"""
    try:
        data = request.get_json()
        portfolio_data = data.get('portfolio', [])
        risk_tolerance = data.get('risk_tolerance', 'moderate')
        
        recommendations = portfolio_analyzer.get_stock_recommendations(portfolio_data, risk_tolerance)
        return jsonify(recommendations)
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        return jsonify({'error': 'Failed to get recommendations'}), 500

@app.route('/portfolio/stock-info/<symbol>', methods=['GET'])
def get_stock_info(symbol):
    """Get detailed stock information"""
    try:
        info = portfolio_analyzer.get_stock_info(symbol)
        if info:
            return jsonify(info)
        else:
            return jsonify({'error': 'Stock not found'}), 404
            
    except Exception as e:
        logger.error(f"Error getting stock info for {symbol}: {str(e)}")
        return jsonify({'error': 'Failed to get stock info'}), 500

@app.route('/portfolio/risk-metrics/<symbol>', methods=['GET'])
def get_stock_risk_metrics(symbol):
    """Get risk metrics for a specific stock"""
    try:
        data = portfolio_analyzer.get_real_stock_data(symbol)
        if data is not None and 'Returns' in data.columns:
            risk_metrics = portfolio_analyzer.calculate_risk_metrics(data['Returns'])
            return jsonify({
                'symbol': symbol,
                'risk_metrics': risk_metrics,
                'current_price': data['Close'].iloc[-1],
                'analysis_date': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': 'Unable to calculate risk metrics'}), 404
            
    except Exception as e:
        logger.error(f"Error getting risk metrics for {symbol}: {str(e)}")
        return jsonify({'error': 'Failed to get risk metrics'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True) 