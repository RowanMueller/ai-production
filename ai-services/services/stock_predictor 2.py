import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
import ta
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
        """Fetch stock data from Yahoo Finance"""
        try:
            if symbol in self.data_cache:
                return self.data_cache[symbol]
            
            stock = yf.Ticker(symbol)
            data = stock.history(period=period)
            
            if data.empty:
                raise ValueError(f"No data found for {symbol}")
            
            # Add technical indicators
            data['SMA_20'] = ta.trend.sma_indicator(data['Close'], window=20)
            data['SMA_50'] = ta.trend.sma_indicator(data['Close'], window=50)
            data['RSI'] = ta.momentum.rsi(data['Close'], window=14)
            data['MACD'] = ta.trend.macd_diff(data['Close'])
            data['BB_upper'], data['BB_middle'], data['BB_lower'] = ta.volatility.bollinger_bands(data['Close'])
            
            # Add price changes
            data['Price_Change'] = data['Close'].pct_change()
            data['Volume_Change'] = data['Volume'].pct_change()
            
            # Remove NaN values
            data = data.dropna()
            
            self.data_cache[symbol] = data
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
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
    
    def build_lstm_model(self, input_shape):
        """Build LSTM model"""
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(25),
            Dense(1)
        ])
        
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
        return model
    
    def train_model(self, symbol, model_type='lstm'):
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
            
            if model_type == 'lstm':
                model = self.build_lstm_model((X.shape[1], X.shape[2]))
                model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.1, verbose=0)
                
            elif model_type == 'linear':
                model = LinearRegression()
                X_train_reshaped = X_train.reshape(X_train.shape[0], -1)
                X_test_reshaped = X_test.reshape(X_test.shape[0], -1)
                model.fit(X_train_reshaped, y_train)
                
            elif model_type == 'ensemble':
                model = RandomForestRegressor(n_estimators=100, random_state=42)
                X_train_reshaped = X_train.reshape(X_train.shape[0], -1)
                X_test_reshaped = X_test.reshape(X_test.shape[0], -1)
                model.fit(X_train_reshaped, y_train)
            
            # Evaluate model
            if model_type == 'lstm':
                y_pred = model.predict(X_test)
            else:
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
                'model_type': model_type,
                'symbol': symbol,
                'mse': mse,
                'mae': mae,
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            }
            
        except Exception as e:
            logger.error(f"Error training model for {symbol}: {str(e)}")
            raise
    
    def predict(self, symbol, days=7, model_type='lstm'):
        """Predict stock prices"""
        try:
            # Get or train model
            model_key = f"{symbol}_{model_type}"
            if model_key not in self.models:
                self.train_model(symbol, model_type)
            
            data = self.get_stock_data(symbol)
            model_info = self.models[model_key]
            model = model_info['model']
            scaler = model_info['scaler']
            
            # Prepare recent data
            features = ['Open', 'High', 'Low', 'Close', 'Volume', 'SMA_20', 'SMA_50', 
                       'RSI', 'MACD', 'BB_upper', 'BB_middle', 'BB_lower', 
                       'Price_Change', 'Volume_Change']
            
            recent_data = data[features].tail(60).values
            scaled_data = scaler.transform(recent_data)
            
            predictions = []
            current_data = scaled_data.copy()
            
            for _ in range(days):
                if model_type == 'lstm':
                    X = current_data[-60:].reshape(1, 60, len(features))
                    pred = model.predict(X, verbose=0)[0, 0]
                else:
                    X = current_data[-60:].reshape(1, -1)
                    pred = model.predict(X)[0]
                
                # Inverse transform prediction
                pred_reshaped = np.zeros((1, len(features)))
                pred_reshaped[0, 3] = pred  # Close price index
                pred_price = scaler.inverse_transform(pred_reshaped)[0, 3]
                
                predictions.append(pred_price)
                
                # Update current_data for next prediction
                new_row = current_data[-1].copy()
                new_row[3] = pred  # Update close price
                current_data = np.vstack([current_data, new_row])
            
            # Calculate confidence based on model metrics
            confidence = max(0.1, 1 - model_info['metrics']['mae'] / data['Close'].mean())
            
            return {
                'symbol': symbol,
                'predictions': predictions,
                'dates': [(datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d') for i in range(days)],
                'model_type': model_type,
                'confidence': confidence,
                'current_price': data['Close'].iloc[-1],
                'prediction_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error predicting {symbol}: {str(e)}")
            raise
    
    def get_history(self, symbol, period='1y'):
        """Get historical stock data"""
        try:
            data = self.get_stock_data(symbol, period)
            
            return {
                'symbol': symbol,
                'data': data.reset_index().to_dict('records'),
                'period': period,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting history for {symbol}: {str(e)}")
            raise
    
    def analyze_stock(self, symbol):
        """Get comprehensive stock analysis"""
        try:
            data = self.get_stock_data(symbol)
            
            # Calculate technical indicators
            current_price = data['Close'].iloc[-1]
            sma_20 = data['SMA_20'].iloc[-1]
            sma_50 = data['SMA_50'].iloc[-1]
            rsi = data['RSI'].iloc[-1]
            
            # Price trends
            price_change_1d = ((current_price - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
            price_change_1w = ((current_price - data['Close'].iloc[-6]) / data['Close'].iloc[-6]) * 100
            price_change_1m = ((current_price - data['Close'].iloc[-21]) / data['Close'].iloc[-21]) * 100
            
            # Support and resistance levels
            support_level = data['Low'].tail(20).min()
            resistance_level = data['High'].tail(20).max()
            
            # Volume analysis
            avg_volume = data['Volume'].tail(20).mean()
            current_volume = data['Volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume
            
            analysis = {
                'symbol': symbol,
                'current_price': current_price,
                'price_changes': {
                    '1d': price_change_1d,
                    '1w': price_change_1w,
                    '1m': price_change_1m
                },
                'technical_indicators': {
                    'sma_20': sma_20,
                    'sma_50': sma_50,
                    'rsi': rsi,
                    'price_vs_sma20': 'above' if current_price > sma_20 else 'below',
                    'price_vs_sma50': 'above' if current_price > sma_50 else 'below'
                },
                'support_resistance': {
                    'support': support_level,
                    'resistance': resistance_level,
                    'distance_to_support': ((current_price - support_level) / current_price) * 100,
                    'distance_to_resistance': ((resistance_level - current_price) / current_price) * 100
                },
                'volume_analysis': {
                    'current_volume': current_volume,
                    'average_volume': avg_volume,
                    'volume_ratio': volume_ratio
                },
                'analysis_date': datetime.now().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {str(e)}")
            raise
    
    def get_sentiment(self, symbol):
        """Get market sentiment analysis"""
        try:
            data = self.get_stock_data(symbol)
            
            # Calculate sentiment indicators
            rsi = data['RSI'].iloc[-1]
            macd = data['MACD'].iloc[-1]
            price_vs_sma20 = data['Close'].iloc[-1] > data['SMA_20'].iloc[-1]
            price_vs_sma50 = data['Close'].iloc[-1] > data['SMA_50'].iloc[-1]
            
            # Sentiment score calculation
            sentiment_score = 0
            
            # RSI sentiment
            if rsi < 30:
                sentiment_score += 2  # Oversold - bullish
            elif rsi > 70:
                sentiment_score -= 2  # Overbought - bearish
            else:
                sentiment_score += 0
            
            # MACD sentiment
            if macd > 0:
                sentiment_score += 1
            else:
                sentiment_score -= 1
            
            # Moving average sentiment
            if price_vs_sma20:
                sentiment_score += 1
            if price_vs_sma50:
                sentiment_score += 1
            
            # Normalize sentiment score
            sentiment_score = max(-5, min(5, sentiment_score))
            sentiment_level = 'bullish' if sentiment_score > 1 else 'bearish' if sentiment_score < -1 else 'neutral'
            
            return {
                'symbol': symbol,
                'sentiment_score': sentiment_score,
                'sentiment_level': sentiment_level,
                'indicators': {
                    'rsi': rsi,
                    'macd': macd,
                    'price_vs_sma20': price_vs_sma20,
                    'price_vs_sma50': price_vs_sma50
                },
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting sentiment for {symbol}: {str(e)}")
            raise
    
    def get_recommendations(self, portfolio_data):
        """Get portfolio recommendations"""
        try:
            # This is a simplified recommendation system
            # In a real application, you would implement more sophisticated logic
            
            recommendations = {
                'buy': [],
                'sell': [],
                'hold': [],
                'diversification': [],
                'risk_assessment': 'medium',
                'recommendation_date': datetime.now().isoformat()
            }
            
            # Add some sample recommendations
            recommendations['buy'].append({
                'symbol': 'AAPL',
                'reason': 'Strong technical indicators and positive momentum',
                'confidence': 0.8
            })
            
            recommendations['hold'].append({
                'symbol': 'MSFT',
                'reason': 'Stable performance, good for long-term holding',
                'confidence': 0.7
            })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            raise 