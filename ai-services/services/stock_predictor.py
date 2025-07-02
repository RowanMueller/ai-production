import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
from datetime import datetime, timedelta
import logging
import joblib
import os

logger = logging.getLogger(__name__)

class StockPredictor:
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.models = {}
        self.data_cache = {}
        self.popular_stocks = [
            'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
            'ADBE', 'CRM', 'ORCL', 'INTC', 'AMD', 'IBM', 'CSCO', 'QCOM',
            'PYPL', 'V', 'MA', 'JPM', 'BAC', 'WMT', 'HD', 'DIS'
        ]
        
        # Create models directory if it doesn't exist
        os.makedirs('models', exist_ok=True)
        
    def get_available_stocks(self):
        """Get list of available stocks"""
        return {
            'stocks': self.popular_stocks,
            'total': len(self.popular_stocks),
            'last_updated': datetime.now().isoformat()
        }
    
    def get_stock_data(self, symbol, period='1y'):
        """Generate mock stock data for demonstration"""
        try:
            if symbol in self.data_cache:
                return self.data_cache[symbol]
            
            # Generate realistic mock data
            np.random.seed(hash(symbol) % 1000)  # Consistent data for each symbol
            
            # Generate dates
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
            
            # Generate price data with realistic patterns
            base_price = 100 + (hash(symbol) % 200)  # Different base price per symbol
            price_trend = np.linspace(0, np.random.normal(0.1, 0.05), len(dates))  # Slight upward trend
            volatility = 0.02
            
            # Generate OHLCV data
            close_prices = base_price * (1 + price_trend + np.cumsum(np.random.normal(0, volatility, len(dates))))
            
            # Generate other OHLC data
            daily_volatility = 0.015
            open_prices = close_prices * (1 + np.random.normal(0, daily_volatility, len(dates)))
            high_prices = np.maximum(open_prices, close_prices) * (1 + np.abs(np.random.normal(0, daily_volatility, len(dates))))
            low_prices = np.minimum(open_prices, close_prices) * (1 - np.abs(np.random.normal(0, daily_volatility, len(dates))))
            
            # Generate volume data
            base_volume = 1000000 + (hash(symbol) % 5000000)
            volumes = base_volume * (1 + np.random.normal(0, 0.3, len(dates)))
            volumes = np.maximum(volumes, 100000)  # Minimum volume
            
            # Create DataFrame
            data = pd.DataFrame({
                'Open': open_prices,
                'High': high_prices,
                'Low': low_prices,
                'Close': close_prices,
                'Volume': volumes
            }, index=dates)
            
            # Add technical indicators
            data['SMA_20'] = data['Close'].rolling(window=20).mean()
            data['SMA_50'] = data['Close'].rolling(window=50).mean()
            
            # Simple RSI calculation
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            data['RSI'] = 100 - (100 / (1 + rs))
            
            # Simple MACD calculation
            exp1 = data['Close'].ewm(span=12).mean()
            exp2 = data['Close'].ewm(span=26).mean()
            data['MACD'] = exp1 - exp2
            
            # Simple Bollinger Bands calculation
            data['BB_middle'] = data['Close'].rolling(window=20).mean()
            bb_std = data['Close'].rolling(window=20).std()
            data['BB_upper'] = data['BB_middle'] + (bb_std * 2)
            data['BB_lower'] = data['BB_middle'] - (bb_std * 2)
            
            # Add price changes
            data['Price_Change'] = data['Close'].pct_change()
            data['Volume_Change'] = data['Volume'].pct_change()
            
            # Remove NaN values
            data = data.dropna()
            
            self.data_cache[symbol] = data
            return data
            
        except Exception as e:
            logger.error(f"Error generating data for {symbol}: {str(e)}")
            raise
    
    def prepare_data(self, data, lookback=60):
        """Prepare data for ML models"""
        # Select features
        features = ['Open', 'High', 'Low', 'Close', 'Volume', 'SMA_20', 'SMA_50', 
                   'RSI', 'MACD', 'BB_upper', 'BB_middle', 'BB_lower', 
                   'Price_Change', 'Volume_Change']
        
        # Scale the data
        scaled_data = self.scaler.fit_transform(data[features])
        
        X, y = [], []
        for i in range(lookback, len(scaled_data)):
            X.append(scaled_data[i-lookback:i])
            y.append(scaled_data[i, 3])  # Close price index
        
        return np.array(X), np.array(y)
    
    def train_model(self, symbol, model_type='linear'):
        """Train ML model for stock prediction"""
        try:
            data = self.get_stock_data(symbol)
            X, y = self.prepare_data(data)
            
            if len(X) < 100:
                raise ValueError("Insufficient data for training")
            
            # Split data
            split = int(len(X) * 0.8)
            X_train, X_test = X[:split], X[split:]
            y_train, y_test = y[:split], y[split:]
            
            if model_type == 'linear':
                model = LinearRegression()
                X_train_reshaped = X_train.reshape(X_train.shape[0], -1)
                X_test_reshaped = X_test.reshape(X_test.shape[0], -1)
                model.fit(X_train_reshaped, y_train)
                
            elif model_type == 'ensemble':
                model = RandomForestRegressor(n_estimators=100, random_state=42)
                X_train_reshaped = X_train.reshape(X_train.shape[0], -1)
                X_test_reshaped = X_test.reshape(X_test.shape[0], -1)
                model.fit(X_train_reshaped, y_train)
            else:
                raise ValueError(f"Unsupported model type: {model_type}")
            
            # Evaluate model
            y_pred = model.predict(X_test_reshaped)
            
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            
            # Save model
            model_key = f"{symbol}_{model_type}"
            self.models[model_key] = {
                'model': model,
                'scaler': self.scaler,
                'metrics': {'mse': mse, 'mae': mae},
                'last_trained': datetime.now()
            }
            
            # Save to disk
            joblib.dump(self.models[model_key], f'models/{model_key}.pkl')
            
            return {
                'symbol': symbol,
                'model_type': model_type,
                'metrics': {'mse': mse, 'mae': mae},
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Error training model for {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'model_type': model_type,
                'error': str(e),
                'status': 'error'
            }
    
    def predict(self, symbol, days=7, model_type='linear'):
        """Predict stock prices"""
        try:
            # Load or train model
            model_key = f"{symbol}_{model_type}"
            if model_key not in self.models:
                # Try to load from disk
                model_path = f'models/{model_key}.pkl'
                if os.path.exists(model_path):
                    self.models[model_key] = joblib.load(model_path)
                else:
                    # Train new model
                    self.train_model(symbol, model_type)
            
            if model_key not in self.models:
                raise ValueError(f"Failed to load or train model for {symbol}")
            
            # Get recent data
            data = self.get_stock_data(symbol)
            recent_data = data.tail(60)  # Last 60 days
            
            # Prepare features
            features = ['Open', 'High', 'Low', 'Close', 'Volume', 'SMA_20', 'SMA_50', 
                       'RSI', 'MACD', 'BB_upper', 'BB_middle', 'BB_lower', 
                       'Price_Change', 'Volume_Change']
            
            # Scale the data
            scaled_data = self.models[model_key]['scaler'].transform(recent_data[features])
            
            # Make predictions
            model = self.models[model_key]['model']
            predictions = []
            
            current_data = scaled_data[-1:].reshape(1, -1)
            for _ in range(days):
                pred = model.predict(current_data)[0]
                predictions.append(pred)
                
                # Update current_data for next prediction (simplified)
                current_data = np.roll(current_data, -1, axis=1)
                current_data[0, -1] = pred
            
            # Inverse transform predictions
            predictions = self.models[model_key]['scaler'].inverse_transform(
                np.array(predictions).reshape(-1, 1)
            )[:, 0]
            
            # Generate dates for predictions
            last_date = data.index[-1]
            pred_dates = [last_date + timedelta(days=i+1) for i in range(days)]
            
            return {
                'symbol': symbol,
                'predictions': [
                    {
                        'date': date.strftime('%Y-%m-%d'),
                        'price': float(price)
                    }
                    for date, price in zip(pred_dates, predictions)
                ],
                'current_price': float(data['Close'].iloc[-1]),
                'model_type': model_type,
                'confidence': 0.75  # Mock confidence score
            }
            
        except Exception as e:
            logger.error(f"Error predicting for {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'error': str(e),
                'status': 'error'
            }
    
    def get_history(self, symbol, period='1y'):
        """Get historical data for a stock"""
        try:
            data = self.get_stock_data(symbol)
            
            return {
                'symbol': symbol,
                'data': data.reset_index().to_dict('records'),
                'period': period,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting history for {symbol}: {str(e)}")
            return {'error': str(e)}
    
    def analyze_stock(self, symbol):
        """Analyze stock performance and provide insights"""
        try:
            data = self.get_stock_data(symbol)
            
            # Calculate basic statistics
            current_price = data['Close'].iloc[-1]
            price_change = data['Close'].pct_change().iloc[-1]
            price_change_7d = (data['Close'].iloc[-1] / data['Close'].iloc[-8] - 1) if len(data) > 7 else 0
            price_change_30d = (data['Close'].iloc[-1] / data['Close'].iloc[-31] - 1) if len(data) > 30 else 0
            
            # Technical indicators
            sma_20 = data['SMA_20'].iloc[-1]
            sma_50 = data['SMA_50'].iloc[-1]
            rsi = data['RSI'].iloc[-1]
            
            # Volume analysis
            avg_volume = data['Volume'].mean()
            current_volume = data['Volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume
            
            # Volatility
            volatility = data['Price_Change'].std() * np.sqrt(252)
            
            # Generate insights
            insights = []
            
            if current_price > sma_20 > sma_50:
                insights.append("Strong uptrend: Price above both 20-day and 50-day moving averages")
            elif current_price < sma_20 < sma_50:
                insights.append("Strong downtrend: Price below both 20-day and 50-day moving averages")
            elif current_price > sma_20 and sma_20 < sma_50:
                insights.append("Potential trend reversal: Price above 20-day MA but below 50-day MA")
            
            if rsi > 70:
                insights.append("Overbought conditions: RSI above 70")
            elif rsi < 30:
                insights.append("Oversold conditions: RSI below 30")
            
            if volume_ratio > 1.5:
                insights.append("High volume: Current volume significantly above average")
            elif volume_ratio < 0.5:
                insights.append("Low volume: Current volume significantly below average")
            
            return {
                'symbol': symbol,
                'current_price': float(current_price),
                'price_change': float(price_change),
                'price_change_7d': float(price_change_7d),
                'price_change_30d': float(price_change_30d),
                'sma_20': float(sma_20),
                'sma_50': float(sma_50),
                'rsi': float(rsi),
                'volume_ratio': float(volume_ratio),
                'volatility': float(volatility),
                'insights': insights,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {str(e)}")
            return {'error': str(e)}
    
    def get_sentiment(self, symbol):
        """Get sentiment analysis for a stock (mock implementation)"""
        try:
            # Mock sentiment analysis
            sentiments = ['positive', 'neutral', 'negative']
            weights = [0.4, 0.4, 0.2]  # Slightly biased towards positive
            
            sentiment = np.random.choice(sentiments, p=weights)
            confidence = np.random.uniform(0.6, 0.9)
            
            # Generate mock news headlines
            headlines = [
                f"{symbol} reports strong quarterly earnings",
                f"Analysts upgrade {symbol} stock rating",
                f"{symbol} announces new product launch",
                f"Market volatility affects {symbol} performance",
                f"{symbol} faces regulatory challenges"
            ]
            
            return {
                'symbol': symbol,
                'sentiment': sentiment,
                'confidence': float(confidence),
                'headlines': np.random.choice(headlines, size=3, replace=False).tolist(),
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting sentiment for {symbol}: {str(e)}")
            return {'error': str(e)}
    
    def get_recommendations(self, portfolio_data):
        """Get stock recommendations based on portfolio"""
        try:
            # Mock recommendations
            recommendations = []
            
            # Popular stocks for diversification
            popular_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'JNJ', 'V']
            
            current_symbols = {item['symbol'] for item in portfolio_data}
            
            for symbol in popular_stocks:
                if symbol not in current_symbols and len(recommendations) < 5:
                    data = self.get_stock_data(symbol)
                    current_price = data['Close'].iloc[-1]
                    
                    recommendations.append({
                        'symbol': symbol,
                        'name': f"{symbol} Corporation",
                        'current_price': float(current_price),
                        'reason': f"Add {symbol} for portfolio diversification",
                        'confidence': float(np.random.uniform(0.7, 0.9))
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return [] 