#!/usr/bin/env python3
"""
Create Sample Data for Enhanced Chatbot
This script creates sample data files for demonstration purposes
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import random

def create_sample_stock_data(symbol: str) -> dict:
    """Create sample stock data for a symbol"""
    base_price = 100 + (hash(symbol) % 200)
    current_price = base_price + random.uniform(-20, 20)
    
    return {
        'symbol': symbol,
        'company_info': {
            'longName': f'{symbol} Corporation',
            'shortName': symbol,
            'currentPrice': round(current_price, 2),
            'marketCap': random.randint(1000000000, 5000000000),
            'trailingPE': round(random.uniform(10, 50), 2),
            'fiftyTwoWeekLow': round(current_price * 0.7, 2),
            'fiftyTwoWeekHigh': round(current_price * 1.5, 2),
            'longBusinessSummary': f'{symbol} is a leading technology company that specializes in innovative solutions for the modern digital economy. The company has shown strong growth potential and maintains a solid market position.',
            'sector': 'Technology',
            'industry': 'Software',
            'website': f'https://www.{symbol.lower()}.com',
            'country': 'United States'
        },
        'historical_data': [
            {
                'Date': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'),
                'Close': round(current_price + random.uniform(-5, 5), 2),
                'Volume': random.randint(1000000, 5000000)
            } for i in range(30, 0, -1)
        ],
        'financials': {
            'revenue': random.randint(10000000000, 100000000000),
            'net_income': random.randint(1000000000, 20000000000),
            'total_assets': random.randint(50000000000, 200000000000)
        },
        'recommendations': [
            {
                'date': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'),
                'recommendation': random.choice(['Buy', 'Hold', 'Sell']),
                'price_target': round(current_price * random.uniform(0.8, 1.3), 2)
            } for i in range(10, 0, -1)
        ],
        'collected_at': datetime.now().isoformat()
    }

def create_sample_news_data(symbol: str) -> list:
    """Create sample news data for a symbol"""
    news_templates = [
        f"{symbol} reports strong quarterly earnings, beating analyst expectations",
        f"New product launch from {symbol} shows promising market potential",
        f"{symbol} announces strategic partnership to expand market reach",
        f"Analysts upgrade {symbol} stock rating based on growth prospects",
        f"{symbol} demonstrates innovation leadership in latest technology showcase",
        f"Market analysts remain bullish on {symbol} despite market volatility",
        f"{symbol} expands into new markets with aggressive growth strategy",
        f"Investors show confidence in {symbol} management team decisions"
    ]
    
    return [
        {
            'title': random.choice(news_templates),
            'description': f"Latest developments in {symbol} stock and company performance.",
            'content': f"Detailed analysis of {symbol} recent performance and future outlook.",
            'published_at': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
            'source': random.choice(['Reuters', 'Bloomberg', 'CNBC', 'MarketWatch', 'Yahoo Finance']),
            'url': f"https://example.com/news/{symbol.lower()}-{i}",
            'symbol': symbol
        } for i in range(random.randint(5, 15))
    ]

def create_sample_market_data() -> dict:
    """Create sample market data"""
    return {
        '^GSPC': {  # S&P 500
            'info': {
                'longName': 'S&P 500',
                'currentPrice': 4500 + random.uniform(-100, 100)
            },
            'historical': [
                {
                    'Date': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'),
                    'Close': 4500 + random.uniform(-50, 50),
                    'Volume': random.randint(1000000000, 3000000000)
                } for i in range(30, 0, -1)
            ]
        },
        '^DJI': {  # Dow Jones
            'info': {
                'longName': 'Dow Jones Industrial Average',
                'currentPrice': 35000 + random.uniform(-500, 500)
            },
            'historical': [
                {
                    'Date': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'),
                    'Close': 35000 + random.uniform(-200, 200),
                    'Volume': random.randint(500000000, 1500000000)
                } for i in range(30, 0, -1)
            ]
        },
        '^IXIC': {  # NASDAQ
            'info': {
                'longName': 'NASDAQ Composite',
                'currentPrice': 14000 + random.uniform(-300, 300)
            },
            'historical': [
                {
                    'Date': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'),
                    'Close': 14000 + random.uniform(-150, 150),
                    'Volume': random.randint(800000000, 2500000000)
                } for i in range(30, 0, -1)
            ]
        },
        '^VIX': {  # VIX
            'info': {
                'longName': 'CBOE Volatility Index',
                'currentPrice': 15 + random.uniform(-5, 10)
            },
            'historical': [
                {
                    'Date': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'),
                    'Close': 15 + random.uniform(-3, 8),
                    'Volume': random.randint(100000, 500000)
                } for i in range(30, 0, -1)
            ]
        }
    }

def create_sample_economic_data() -> dict:
    """Create sample economic indicators"""
    return {
        'GDP': [
            {
                'date': (datetime.now() - timedelta(days=i*30)).strftime('%Y-%m-%d'),
                'value': 25000 + random.uniform(-500, 500)
            } for i in range(12, 0, -1)
        ],
        'UNRATE': [
            {
                'date': (datetime.now() - timedelta(days=i*30)).strftime('%Y-%m-%d'),
                'value': 3.5 + random.uniform(-0.5, 0.5)
            } for i in range(12, 0, -1)
        ],
        'CPIAUCSL': [
            {
                'date': (datetime.now() - timedelta(days=i*30)).strftime('%Y-%m-%d'),
                'value': 300 + random.uniform(-10, 10)
            } for i in range(12, 0, -1)
        ],
        'FEDFUNDS': [
            {
                'date': (datetime.now() - timedelta(days=i*30)).strftime('%Y-%m-%d'),
                'value': 5.25 + random.uniform(-0.25, 0.25)
            } for i in range(12, 0, -1)
        ],
        'DGS10': [
            {
                'date': (datetime.now() - timedelta(days=i*30)).strftime('%Y-%m-%d'),
                'value': 4.5 + random.uniform(-0.5, 0.5)
            } for i in range(12, 0, -1)
        ]
    }

def create_sample_prompt_templates() -> dict:
    """Create sample prompt templates"""
    return {
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

**Technical Indicators:**
- RSI: {rsi}
- MACD: {macd}
- Moving Averages: {ma_status}

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
            'variables': ['symbol', 'current_price', 'low_52wk', 'high_52wk', 'market_cap', 'pe_ratio', 'rsi', 'macd', 'ma_status', 'sp500_change', 'vix_value', 'interest_rate', 'inflation_rate']
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

def main():
    """Create sample data for all directories"""
    data_dir = Path("data")
    
    # Create directories
    for subdir in ['stocks', 'news', 'economic', 'prompts']:
        (data_dir / subdir).mkdir(parents=True, exist_ok=True)
    
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'ADBE', 'CRM']
    
    print("Creating sample data...")
    
    # Create stock data
    for symbol in symbols:
        stock_data = create_sample_stock_data(symbol)
        with open(data_dir / "stocks" / f"{symbol}_data.json", 'w') as f:
            json.dump(stock_data, f, indent=2, default=str)
        print(f"Created stock data for {symbol}")
    
    # Create news data
    for symbol in symbols:
        news_data = create_sample_news_data(symbol)
        with open(data_dir / "news" / f"{symbol}_news.json", 'w') as f:
            json.dump(news_data, f, indent=2, default=str)
        print(f"Created news data for {symbol}")
    
    # Create market data
    market_data = create_sample_market_data()
    with open(data_dir / "economic" / "market_data.json", 'w') as f:
        json.dump(market_data, f, indent=2, default=str)
    print("Created market data")
    
    # Create economic data
    economic_data = create_sample_economic_data()
    with open(data_dir / "economic" / "economic_indicators.json", 'w') as f:
        json.dump(economic_data, f, indent=2, default=str)
    print("Created economic data")
    
    # Create prompt templates
    prompt_templates = create_sample_prompt_templates()
    with open(data_dir / "prompts" / "templates.json", 'w') as f:
        json.dump(prompt_templates, f, indent=2, default=str)
    print("Created prompt templates")
    
    print("\nSample data creation completed!")
    print("You can now use the enhanced chatbot with comprehensive sample data.")

if __name__ == "__main__":
    main() 