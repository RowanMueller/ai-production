import re
import random
import json
import os
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Any
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

class EnhancedChatbot:
    def __init__(self, stock_predictor=None, task_prioritizer=None, data_dir="data"):
        self.stock_predictor = stock_predictor
        self.task_prioritizer = task_prioritizer
        self.data_dir = Path(data_dir)
        
        # Load prompt templates
        self.prompt_templates = self.load_prompt_templates()
        
        # Intent patterns (same as original)
        self.intent_patterns = {
            'greeting': [
                r'\b(hi|hello|hey|greetings|good morning|good afternoon|good evening)\b',
                r'\bhow are you\b',
                r'\bnice to meet you\b'
            ],
            'stock_info': [
                r'\b(tell me about|info|information|data|details|what is|what\'s)\s+([A-Z]{1,5})\b',
                r'\b([A-Z]{1,5})\s+(price|value|worth|trading at)\b',
                r'\bcurrent\s+(price|value)\s+of\s+([A-Z]{1,5})\b'
            ],
            'stock_prediction': [
                r'\b(predict|forecast|future|tomorrow|next week|next month)\s+(price|value)\s+(of\s+)?([A-Z]{1,5})\b',
                r'\b([A-Z]{1,5})\s+(prediction|forecast|future)\b',
                r'\bwhat\s+will\s+([A-Z]{1,5})\s+(be|cost|worth)\b'
            ],
            'stock_analysis': [
                r'\b(analyze|analysis|trend|technical|indicator)\s+(of\s+)?([A-Z]{1,5})\b',
                r'\b([A-Z]{1,5})\s+(analysis|trend|performance)\b',
                r'\bhow\s+is\s+([A-Z]{1,5})\s+(performing|doing)\b'
            ],
            'market_sentiment': [
                r'\b(sentiment|mood|feeling)\s+(about|for)\s+([A-Z]{1,5})\b',
                r'\b([A-Z]{1,5})\s+(sentiment|mood)\b',
                r'\bmarket\s+(sentiment|mood)\s+(for\s+)?([A-Z]{1,5})\b'
            ],
            'portfolio_advice': [
                r'\b(portfolio|investment|invest|buy|sell|hold)\s+(advice|recommendation)\b',
                r'\bshould\s+I\s+(buy|sell|hold)\s+([A-Z]{1,5})\b',
                r'\b(buy|sell|hold)\s+([A-Z]{1,5})\b'
            ],
            'help': [
                r'\b(help|what can you do|capabilities|features|assist)\b',
                r'\bhow\s+can\s+you\s+help\b',
                r'\bwhat\s+do\s+you\s+do\b'
            ],
            'goodbye': [
                r'\b(bye|goodbye|see you|thanks|thank you|exit|quit)\b'
            ]
        }
        
        self.stock_symbols = [
            'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
            'ADBE', 'CRM', 'ORCL', 'INTC', 'AMD', 'IBM', 'CSCO', 'QCOM',
            'PYPL', 'V', 'MA', 'JPM', 'BAC', 'WMT', 'HD', 'DIS'
        ]
    
    def load_prompt_templates(self) -> Dict:
        """Load prompt templates from data directory"""
        template_file = self.data_dir / "prompts" / "templates.json"
        if template_file.exists():
            try:
                with open(template_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading prompt templates: {str(e)}")
        
        # Return default templates if file doesn't exist
        return {
            'stock_analysis': {
                'context': "You are a financial analyst assistant. Use the following data to provide insights:",
                'prompt_template': """
Based on the following data for {symbol}:

**Stock Data:**
- Current Price: ${current_price}
- 52-Week Range: ${low_52wk} - ${high_52wk}
- Market Cap: ${market_cap}
- P/E Ratio: {pe_ratio}

**Technical Indicators:**
- RSI: {rsi}
- MACD: {macd}
- Moving Averages: {ma_status}

**Market Context:**
- S&P 500: {sp500_change}%
- Market Volatility (VIX): {vix_value}

Provide a comprehensive analysis including:
1. Technical analysis
2. Fundamental analysis
3. Risk assessment
4. Investment recommendation
""",
                'variables': ['symbol', 'current_price', 'low_52wk', 'high_52wk', 'market_cap', 'pe_ratio', 'rsi', 'macd', 'ma_status', 'sp500_change', 'vix_value']
            }
        }
    
    def load_stock_data(self, symbol: str) -> Optional[Dict]:
        """Load collected stock data for a symbol"""
        try:
            stock_file = self.data_dir / "stocks" / f"{symbol}_data.json"
            if stock_file.exists():
                with open(stock_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading stock data for {symbol}: {str(e)}")
        return None
    
    def load_news_data(self, symbol: str) -> List[Dict]:
        """Load collected news data for a symbol"""
        try:
            news_file = self.data_dir / "news" / f"{symbol}_news.json"
            if news_file.exists():
                with open(news_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading news data for {symbol}: {str(e)}")
        return []
    
    def load_market_data(self) -> Optional[Dict]:
        """Load market data"""
        try:
            market_file = self.data_dir / "economic" / "market_data.json"
            if market_file.exists():
                with open(market_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading market data: {str(e)}")
        return None
    
    def extract_stock_symbol(self, message: str) -> Optional[str]:
        """Extract stock symbol from message using regex patterns"""
        message_upper = message.upper()
        
        # Look for stock symbols in various patterns
        patterns = [
            r'\b([A-Z]{1,5})\b',  # Any 1-5 letter uppercase word
            r'\$([A-Z]{1,5})\b',  # $SYMBOL format
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, message_upper)
            for match in matches:
                symbol = match if isinstance(match, str) else match[0]
                if symbol in self.stock_symbols:
                    return symbol
        
        return None
    
    def classify_intent(self, message: str) -> Dict[str, Any]:
        """Classify user intent using regex patterns"""
        message_lower = message.lower()
        message_upper = message.upper()

        # Improved: check for 'tell me about <SYMBOL>' and similar patterns (case-insensitive, use message_upper)
        stock_info_patterns = [
            r'TELL ME ABOUT\s+([A-Z]{1,5})',
            r'INFO(?:RMATION)?\s+ON\s+([A-Z]{1,5})',
            r'WHAT IS\s+([A-Z]{1,5})',
            r'([A-Z]{1,5})\s+(PRICE|VALUE|WORTH|TRADING AT)',
            r'CURRENT\s+(PRICE|VALUE)\s+OF\s+([A-Z]{1,5})',
        ]
        for pattern in stock_info_patterns:
            match = re.search(pattern, message_upper)
            if match:
                return {
                    'intent': 'stock_info',
                    'confidence': 0.95,
                    'matches': match.groups()
                }

        # Check for analysis patterns
        analysis_patterns = [
            r'ANALYZE\s+([A-Z]{1,5})\s+(PERFORMANCE|TREND|STOCK)',
            r'([A-Z]{1,5})\s+(ANALYSIS|PERFORMANCE|TREND)',
            r'ANALYSIS\s+OF\s+([A-Z]{1,5})',
            r'HOW\s+IS\s+([A-Z]{1,5})\s+(PERFORMING|DOING)',
        ]
        for pattern in analysis_patterns:
            match = re.search(pattern, message_upper)
            if match:
                return {
                    'intent': 'stock_analysis',
                    'confidence': 0.95,
                    'matches': match.groups()
                }

        # Check for prediction patterns
        prediction_patterns = [
            r'PREDICT\s+([A-Z]{1,5})\s+(PRICE|VALUE|FUTURE)',
            r'([A-Z]{1,5})\s+(PREDICTION|FORECAST|FUTURE)',
            r'WHAT\s+WILL\s+([A-Z]{1,5})\s+(BE|COST|WORTH)',
        ]
        for pattern in prediction_patterns:
            match = re.search(pattern, message_upper)
            if match:
                return {
                    'intent': 'stock_prediction',
                    'confidence': 0.95,
                    'matches': match.groups()
                }

        # Existing pattern-based intent detection
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, message_lower)
                if matches:
                    return {
                        'intent': intent,
                        'confidence': 0.9,
                        'matches': matches
                    }
        # Fallback: check for stock-related keywords
        stock_keywords = ['stock', 'price', 'market', 'invest', 'prediction', 'analysis']
        if any(keyword in message_lower for keyword in stock_keywords):
            return {
                'intent': 'stock_general',
                'confidence': 0.6,
                'matches': []
            }
        return {
            'intent': 'unknown',
            'confidence': 0.3,
            'matches': []
        }
    
    def analyze_sentiment(self, message: str) -> str:
        """Simple rule-based sentiment analysis"""
        message_lower = message.lower()
        
        # Positive words
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'positive', 'up', 'rise', 'gain', 'profit', 'success', 'strong', 'bullish']
        
        # Negative words
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'negative', 'down', 'fall', 'drop', 'loss', 'weak', 'bearish', 'crash', 'decline']
        
        # Count positive and negative words
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def analyze_news_sentiment(self, news_data: List[Dict]) -> Dict[str, Any]:
        """Analyze sentiment from collected news data"""
        if not news_data:
            return {'sentiment': 'neutral', 'score': 0.0, 'confidence': 0.0, 'article_count': 0}
        
        sentiments = []
        for article in news_data:
            text = f"{article.get('title', '')} {article.get('description', '')}"
            # Simple rule-based sentiment analysis
            text_lower = text.lower()
            
            # Positive words
            positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'positive', 'up', 'rise', 'gain', 'profit', 'success', 'strong', 'bullish', 'beat', 'surge', 'jump', 'climb']
            
            # Negative words
            negative_words = ['bad', 'terrible', 'awful', 'horrible', 'negative', 'down', 'fall', 'drop', 'loss', 'weak', 'bearish', 'crash', 'decline', 'miss', 'plunge', 'dip', 'slump']
            
            # Count positive and negative words
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                sentiment_score = 0.3
            elif negative_count > positive_count:
                sentiment_score = -0.3
            else:
                sentiment_score = 0.0
            
            sentiments.append(sentiment_score)
        
        avg_sentiment = sum(sentiments) / len(sentiments)
        
        if avg_sentiment > 0.1:
            sentiment_level = 'positive'
        elif avg_sentiment < -0.1:
            sentiment_level = 'negative'
        else:
            sentiment_level = 'neutral'
        
        return {
            'sentiment': sentiment_level,
            'score': round(avg_sentiment, 3),
            'confidence': min(len(sentiments) * 0.1, 0.9),  # More articles = higher confidence
            'article_count': len(sentiments)
        }
    
    def generate_enhanced_response(self, intent: str, symbol: str, context: Dict = None) -> str:
        """Generate enhanced response using collected data and prompt templates"""
        try:
            # Load collected data
            stock_data = self.load_stock_data(symbol)
            news_data = self.load_news_data(symbol)
            market_data = self.load_market_data()
            
            if intent == 'stock_info':
                if stock_data and 'company_info' in stock_data:
                    info = stock_data['company_info']
                    news_sentiment = self.analyze_news_sentiment(news_data)
                    
                    # Get current price from stock predictor
                    current_price = "N/A"
                    if self.stock_predictor:
                        try:
                            live_data = self.stock_predictor.get_stock_data(symbol)
                            current_price = f"${live_data['Close'].iloc[-1]:.2f}"
                        except:
                            pass
                    
                    response = f"""📊 **{symbol} Comprehensive Stock Information**

💰 **Current Price**: {current_price}
🏢 **Company**: {info.get('longName', 'N/A')}
📈 **Market Cap**: ${info.get('marketCap', 0):,}M
📊 **P/E Ratio**: {info.get('trailingPE', 'N/A')}
📅 **52-Week Range**: ${info.get('fiftyTwoWeekLow', 0):.2f} - ${info.get('fiftyTwoWeekHigh', 0):.2f}

📰 **News Sentiment**: {news_sentiment['sentiment'].title()} ({news_sentiment['score']:.2f})
📊 **Articles Analyzed**: {news_sentiment['article_count']}

💡 **Business Summary**: {info.get('longBusinessSummary', 'No summary available.')[:200]}...

Would you like a detailed technical analysis or price prediction for {symbol}?"""
                    
                    return response
            
            elif intent == 'stock_analysis':
                if stock_data and market_data:
                    # Use prompt template for analysis
                    template = self.prompt_templates.get('stock_analysis', {})
                    prompt_template = template.get('prompt_template', '')
                    
                    # Extract data for template
                    info = stock_data.get('company_info', {})
                    current_price = info.get('currentPrice', 0)
                    
                    # Get technical indicators from stock predictor
                    technical_data = {}
                    if self.stock_predictor:
                        try:
                            live_data = self.stock_predictor.get_stock_data(symbol)
                            technical_data = {
                                'rsi': live_data['RSI'].iloc[-1],
                                'macd': live_data['MACD'].iloc[-1],
                                'sma_20': live_data['SMA_20'].iloc[-1],
                                'sma_50': live_data['SMA_50'].iloc[-1]
                            }
                        except:
                            pass
                    
                    # Market context
                    sp500_data = market_data.get('^GSPC', {})
                    sp500_change = 0
                    if sp500_data and 'historical' in sp500_data:
                        hist = sp500_data['historical']
                        if len(hist) >= 2:
                            sp500_change = ((hist[-1]['Close'] - hist[-2]['Close']) / hist[-2]['Close']) * 100
                    
                    response = f"""📈 **{symbol} Technical Analysis**

💰 **Current Price**: ${current_price}
📊 **Technical Indicators**:
   • RSI: {technical_data.get('rsi', 'N/A'):.2f}
   • MACD: {technical_data.get('macd', 'N/A'):.2f}
   • 20-Day SMA: ${technical_data.get('sma_20', 'N/A'):.2f}
   • 50-Day SMA: ${technical_data.get('sma_50', 'N/A'):.2f}

📊 **Market Context**:
   • S&P 500 Change: {sp500_change:.2f}%
   • Market Cap: ${info.get('marketCap', 0):,}M
   • P/E Ratio: {info.get('trailingPE', 'N/A')}

📰 **News Sentiment**: {self.analyze_news_sentiment(news_data)['sentiment'].title()}

💡 **Analysis**: Based on technical indicators and market conditions, {symbol} shows {'bullish' if technical_data.get('rsi', 50) > 50 else 'bearish'} momentum with {'strong' if abs(technical_data.get('rsi', 50) - 50) > 20 else 'moderate'} relative strength."""
                    
                    return response
            
            # Fallback to basic response
            return f"I have comprehensive data for {symbol}. Would you like a detailed analysis, price prediction, or market sentiment overview?"
            
        except Exception as e:
            logger.error(f"Error generating enhanced response: {str(e)}")
            return f"I'm sorry, I encountered an error while analyzing {symbol}. Please try again."
    
    def update_context(self, context: Optional[Dict], intent: str, symbol: Optional[str], sentiment: str) -> Dict[str, Any]:
        """Update conversation context"""
        if context is None or not isinstance(context, dict):
            context = {}
        context.setdefault('user_preferences', {})
        context.setdefault('stock_interests', [])
        context.setdefault('last_query', None)
        context.setdefault('conversation_history', [])
        
        # Update last query
        context['last_query'] = {
            'intent': intent,
            'sentiment': sentiment,
            'symbol': symbol,
            'timestamp': datetime.now().isoformat()
        }
        
        # Track stock interests
        if symbol and symbol not in context['stock_interests']:
            context['stock_interests'].append(symbol)
        
        return context
    
    async def process_message(self, message: str, session_id: Optional[str] = None, 
                            context: Optional[Dict] = None, history: Optional[List] = None) -> Dict[str, Any]:
        """Process incoming chat message with enhanced data integration"""
        try:
            # Analyze message
            intent_data = self.classify_intent(message)
            sentiment = self.analyze_sentiment(message)
            symbol = self.extract_stock_symbol(message)
            
            intent = intent_data['intent']
            confidence = intent_data['confidence']
            
            # Initialize response
            response = ""
            suggestions = []
            
            # Handle different intents with enhanced data integration
            if intent in ['stock_info', 'stock_analysis'] and symbol:
                response = self.generate_enhanced_response(intent, symbol, context)
                suggestions = [
                    f"Get {symbol} price prediction",
                    f"Analyze {symbol} technical indicators",
                    f"Check {symbol} market sentiment",
                    f"Compare {symbol} with competitors"
                ]
            
            elif intent == 'stock_prediction' and symbol:
                # Use stock predictor for predictions
                if self.stock_predictor:
                    try:
                        prediction = self.stock_predictor.predict(symbol, 7, 'lstm')
                        pred_text = "\n".join([f"   • {date}: ${price:.2f}" for date, price in zip(prediction['dates'], prediction['predictions'])])
                        response = f"""🔮 **{symbol} Price Prediction (7 Days)**

💰 **Current Price**: ${prediction['current_price']:.2f}
🎯 **Prediction Confidence**: {prediction['confidence'] * 100:.1f}%

📅 **Forecast**:
{pred_text}

⚠️ **Disclaimer**: These are AI-generated predictions and should not be considered as financial advice."""
                    except Exception as e:
                        response = f"I'm sorry, I couldn't generate a prediction for {symbol} at the moment. Please try again later."
                else:
                    response = f"I'm sorry, the prediction service is not available for {symbol}."
                
                suggestions = [
                    f"Get detailed analysis for {symbol}",
                    f"Check {symbol} market sentiment",
                    f"Get {symbol} technical indicators"
                ]
            
            elif intent == 'market_sentiment' and symbol:
                news_data = self.load_news_data(symbol)
                sentiment_data = self.analyze_news_sentiment(news_data)
                
                response = f"""🎭 **{symbol} Market Sentiment**

📊 **Sentiment Level**: {sentiment_data['sentiment'].title()}
🎯 **Confidence**: {sentiment_data['confidence'] * 100:.1f}%
📈 **Sentiment Score**: {sentiment_data['score']:.3f}
📰 **Articles Analyzed**: {sentiment_data['article_count']}

💡 **Analysis**: Based on recent news coverage, {symbol} has {sentiment_data['sentiment']} market sentiment with {'high' if sentiment_data['confidence'] > 0.7 else 'moderate' if sentiment_data['confidence'] > 0.4 else 'low'} confidence."""
                
                suggestions = [
                    f"Get {symbol} price prediction",
                    f"Analyze {symbol} technical indicators",
                    f"Get {symbol} comprehensive analysis"
                ]
            
            elif intent == 'greeting':
                response = "Hello! I'm your enhanced AI financial assistant with access to comprehensive market data, news sentiment analysis, and technical indicators. I can help you with detailed stock analysis, predictions, and market insights. What would you like to know?"
                suggestions = [
                    "Tell me about AAPL",
                    "Predict TSLA price for next week",
                    "Analyze MSFT performance",
                    "What's the market sentiment for GOOGL?"
                ]
            
            elif intent == 'help':
                response = """I can help you with:

📈 **Enhanced Stock Analysis**: Detailed analysis using real market data, technical indicators, and news sentiment
🔮 **AI Price Predictions**: Machine learning-powered price forecasts with confidence levels
📊 **Market Sentiment**: News sentiment analysis and social media mood tracking
💼 **Investment Insights**: Comprehensive investment recommendations based on multiple data sources
📋 **Task Management**: Help prioritize your investment tasks and research

Try asking me about a specific stock like "Tell me about AAPL" or "Analyze TSLA performance"!"""
                suggestions = [
                    "Tell me about AAPL",
                    "Predict TSLA price",
                    "Analyze MSFT",
                    "Check GOOGL sentiment"
                ]
            
            elif intent == 'goodbye':
                response = "Thank you for chatting with me! Feel free to come back anytime for more financial insights and analysis."
                suggestions = []
            
            elif intent == 'stock_general':
                response = "I can help you with comprehensive stock market analysis and predictions using real-time data, news sentiment, and technical indicators. What specific stock would you like to know about?"
                suggestions = [
                    "Tell me about AAPL",
                    "Predict TSLA price",
                    "Analyze MSFT",
                    "Check GOOGL sentiment"
                ]
            
            else:
                response = "I'm not sure I understand. I'm specialized in stock market analysis with access to comprehensive data. Try asking me about a specific stock like 'Tell me about AAPL' or 'What's the prediction for TSLA?'"
                suggestions = [
                    "Tell me about AAPL",
                    "Predict TSLA price",
                    "Analyze MSFT",
                    "Check GOOGL sentiment"
                ]
            
            # Update context
            updated_context = self.update_context(context, intent, symbol, sentiment)
            
            return {
                'response': response,
                'confidence': confidence,
                'intent': intent,
                'sentiment': sentiment,
                'symbol': symbol,
                'suggestions': suggestions,
                'updatedContext': updated_context,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                'response': "I'm sorry, I encountered an error processing your message. Please try again.",
                'confidence': 0.0,
                'intent': 'error',
                'suggestions': ['Try asking about a specific stock', 'Ask for help to see what I can do'],
                'timestamp': datetime.now().isoformat()
            }
    
    def get_suggestions(self, session_id: str, context: Optional[Dict] = None) -> List[str]:
        """Get contextual suggestions based on session history"""
        if context is None or not isinstance(context, dict):
            context = {}
        context.setdefault('stock_interests', [])
        
        if context['stock_interests']:
            symbols = context['stock_interests'][-3:]  # Last 3 stocks
            suggestions = []
            for symbol in symbols:
                suggestions.extend([
                    f"Get {symbol} price prediction",
                    f"Analyze {symbol} performance",
                    f"Check {symbol} market sentiment"
                ])
            return suggestions[:6]  # Limit to 6 suggestions
        
        return [
            "Tell me about AAPL",
            "Predict TSLA price",
            "Analyze MSFT",
            "Check GOOGL sentiment"
        ] 