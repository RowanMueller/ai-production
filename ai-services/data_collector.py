import os
import json
import pandas as pd
import requests
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import yfinance as yf

logger = logging.getLogger(__name__)

class DataCollector:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.ensure_data_dir()
        
        # API Keys (set these in environment variables)
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_KEY')
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.finnhub_key = os.getenv('FINNHUB_KEY')
        
    def ensure_data_dir(self):
        """Ensure data directory exists"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(f"{self.data_dir}/stocks", exist_ok=True)
        os.makedirs(f"{self.data_dir}/news", exist_ok=True)
        os.makedirs(f"{self.data_dir}/sentiment", exist_ok=True)
        os.makedirs(f"{self.data_dir}/economic", exist_ok=True)
        os.makedirs(f"{self.data_dir}/prompts", exist_ok=True)
    
    def collect_stock_data(self, symbol: str, period: str = "1y") -> Dict:
        """Collect comprehensive stock data"""
        try:
            # Use yfinance for basic data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            # Get company info
            info = ticker.info
            
            # Get financials
            financials = ticker.financials
            balance_sheet = ticker.balance_sheet
            
            # Get analyst recommendations
            recommendations = ticker.recommendations
            
            data = {
                'symbol': symbol,
                'historical_data': hist.to_dict('records'),
                'company_info': info,
                'financials': financials.to_dict() if financials is not None else {},
                'balance_sheet': balance_sheet.to_dict() if balance_sheet is not None else {},
                'recommendations': recommendations.to_dict() if recommendations is not None else {},
                'collected_at': datetime.now().isoformat()
            }
            
            # Save to file
            file_path = f"{self.data_dir}/stocks/{symbol}_data.json"
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"Collected stock data for {symbol}")
            return data
            
        except Exception as e:
            logger.error(f"Error collecting stock data for {symbol}: {str(e)}")
            return {}
    
    def collect_news_data(self, symbol: str, days: int = 30) -> List[Dict]:
        """Collect news articles for sentiment analysis"""
        news_data = []
        
        try:
            # Use NewsAPI if available
            if self.news_api_key:
                url = f"https://newsapi.org/v2/everything"
                params = {
                    'q': f'"{symbol}" AND (stock OR market OR trading)',
                    'from': (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
                    'sortBy': 'publishedAt',
                    'apiKey': self.news_api_key,
                    'language': 'en'
                }
                
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    articles = response.json().get('articles', [])
                    for article in articles:
                        news_data.append({
                            'title': article.get('title'),
                            'description': article.get('description'),
                            'content': article.get('content'),
                            'published_at': article.get('publishedAt'),
                            'source': article.get('source', {}).get('name'),
                            'url': article.get('url'),
                            'symbol': symbol
                        })
            
            # Save news data
            if news_data:
                file_path = f"{self.data_dir}/news/{symbol}_news.json"
                with open(file_path, 'w') as f:
                    json.dump(news_data, f, indent=2, default=str)
                
                logger.info(f"Collected {len(news_data)} news articles for {symbol}")
            
        except Exception as e:
            logger.error(f"Error collecting news for {symbol}: {str(e)}")
        
        return news_data
    
    def collect_market_data(self) -> Dict:
        """Collect broad market data"""
        try:
            # Major indices
            indices = ['^GSPC', '^DJI', '^IXIC', '^VIX']  # S&P 500, Dow, NASDAQ, VIX
            market_data = {}
            
            for index in indices:
                ticker = yf.Ticker(index)
                hist = ticker.history(period="1mo")
                info = ticker.info
                
                market_data[index] = {
                    'historical': hist.to_dict('records'),
                    'info': info,
                    'current_value': hist['Close'].iloc[-1] if not hist.empty else None
                }
            
            # Save market data
            file_path = f"{self.data_dir}/economic/market_data.json"
            with open(file_path, 'w') as f:
                json.dump(market_data, f, indent=2, default=str)
            
            logger.info("Collected market data")
            return market_data
            
        except Exception as e:
            logger.error(f"Error collecting market data: {str(e)}")
            return {}
    
    def collect_economic_data(self) -> Dict:
        """Collect economic indicators"""
        try:
            # FRED API for economic data
            fred_api_key = os.getenv('FRED_API_KEY')
            if fred_api_key:
                indicators = {
                    'GDP': 'GDP',  # Gross Domestic Product
                    'UNRATE': 'UNRATE',  # Unemployment Rate
                    'CPIAUCSL': 'CPIAUCSL',  # Consumer Price Index
                    'FEDFUNDS': 'FEDFUNDS',  # Federal Funds Rate
                    'DGS10': 'DGS10',  # 10-Year Treasury Rate
                }
                
                economic_data = {}
                for name, series_id in indicators.items():
                    url = f"https://api.stlouisfed.org/fred/series/observations"
                    params = {
                        'series_id': series_id,
                        'api_key': fred_api_key,
                        'file_type': 'json',
                        'limit': 100
                    }
                    
                    response = requests.get(url, params=params)
                    if response.status_code == 200:
                        data = response.json()
                        economic_data[name] = data.get('observations', [])
                
                # Save economic data
                file_path = f"{self.data_dir}/economic/economic_indicators.json"
                with open(file_path, 'w') as f:
                    json.dump(economic_data, f, indent=2, default=str)
                
                logger.info("Collected economic data")
                return economic_data
            
        except Exception as e:
            logger.error(f"Error collecting economic data: {str(e)}")
        
        return {}
    
    def generate_prompt_templates(self) -> Dict:
        """Generate prompt templates based on collected data"""
        templates = {
            'stock_analysis': {
                'context': "You are a financial analyst assistant. Use the following data to provide insights:",
                'data_sources': ['stock_data', 'news_data', 'market_data', 'economic_data'],
                'prompt_template': """
Based on the following data for {symbol}:

**Stock Data:**
- Current Price: ${current_price}
- 52-Week Range: ${low_52wk} - ${high_52wk}
- Market Cap: ${market_cap}
- P/E Ratio: {pe_ratio}

**Recent News Sentiment:**
{news_summary}

**Market Context:**
- S&P 500: {sp500_change}%
- Market Volatility (VIX): {vix_value}

**Economic Indicators:**
- Interest Rate: {interest_rate}%
- Inflation Rate: {inflation_rate}%

Provide a comprehensive analysis including:
1. Technical analysis
2. Fundamental analysis
3. Risk assessment
4. Investment recommendation
""",
                'variables': ['symbol', 'current_price', 'low_52wk', 'high_52wk', 'market_cap', 'pe_ratio', 'news_summary', 'sp500_change', 'vix_value', 'interest_rate', 'inflation_rate']
            },
            
            'prediction_prompt': {
                'context': "You are an AI stock prediction model. Analyze the following data:",
                'data_sources': ['historical_data', 'technical_indicators', 'sentiment_data'],
                'prompt_template': """
Given the following data for {symbol}:

**Historical Performance:**
- 30-day return: {return_30d}%
- 90-day return: {return_90d}%
- Volatility: {volatility}%

**Technical Indicators:**
- RSI: {rsi}
- MACD: {macd}
- Moving Averages: {ma_status}

**Market Sentiment:**
- News Sentiment: {news_sentiment}
- Analyst Recommendations: {analyst_recs}

**Market Conditions:**
- Sector Performance: {sector_performance}%
- Market Trend: {market_trend}

Predict the stock price for the next 7 days with confidence level and reasoning.
""",
                'variables': ['symbol', 'return_30d', 'return_90d', 'volatility', 'rsi', 'macd', 'ma_status', 'news_sentiment', 'analyst_recs', 'sector_performance', 'market_trend']
            },
            
            'sentiment_analysis': {
                'context': "You are a market sentiment analyst. Analyze the following news and social media data:",
                'data_sources': ['news_data', 'social_media', 'analyst_reports'],
                'prompt_template': """
Analyze the sentiment for {symbol} based on:

**Recent News Articles ({news_count} articles):**
{news_summary}

**Social Media Mentions:**
- Twitter Sentiment: {twitter_sentiment}
- Reddit Sentiment: {reddit_sentiment}

**Analyst Coverage:**
- Buy Recommendations: {buy_count}
- Hold Recommendations: {hold_count}
- Sell Recommendations: {sell_count}

Provide a sentiment score (1-10) and detailed analysis of market sentiment.
""",
                'variables': ['symbol', 'news_count', 'news_summary', 'twitter_sentiment', 'reddit_sentiment', 'buy_count', 'hold_count', 'sell_count']
            }
        }
        
        # Save prompt templates
        file_path = f"{self.data_dir}/prompts/templates.json"
        with open(file_path, 'w') as f:
            json.dump(templates, f, indent=2)
        
        logger.info("Generated prompt templates")
        return templates
    
    def collect_all_data(self, symbols: List[str] = None):
        """Collect all types of data"""
        if symbols is None:
            symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA']
        
        logger.info(f"Starting data collection for {len(symbols)} symbols")
        
        # Collect stock data
        for symbol in symbols:
            self.collect_stock_data(symbol)
            self.collect_news_data(symbol)
        
        # Collect market and economic data
        self.collect_market_data()
        self.collect_economic_data()
        
        # Generate prompt templates
        self.generate_prompt_templates()
        
        logger.info("Data collection completed")

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize collector
    collector = DataCollector()
    
    # Collect data for major stocks
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'ADBE', 'CRM']
    collector.collect_all_data(symbols) 