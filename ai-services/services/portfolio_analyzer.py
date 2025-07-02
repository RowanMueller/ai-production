import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging
import yfinance as yf
from scipy import stats
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class PortfolioAnalyzer:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.risk_free_rate = 0.04  # 4% risk-free rate (10-year Treasury)
        
        # Risk tolerance levels
        self.risk_levels = {
            'conservative': {'max_volatility': 0.15, 'max_drawdown': 0.10},
            'moderate': {'max_volatility': 0.25, 'max_drawdown': 0.20},
            'aggressive': {'max_volatility': 0.40, 'max_drawdown': 0.35}
        }
    
    def get_real_stock_data(self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """Generate mock stock data for demonstration (replacing real Yahoo Finance calls)"""
        try:
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
            
            # Calculate returns
            data['Returns'] = data['Close'].pct_change()
            data['Log_Returns'] = np.log(data['Close'] / data['Close'].shift(1))
            
            # Calculate technical indicators
            data['SMA_20'] = data['Close'].rolling(window=20).mean()
            data['SMA_50'] = data['Close'].rolling(window=50).mean()
            
            # RSI
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            data['RSI'] = 100 - (100 / (1 + rs))
            
            # MACD
            exp1 = data['Close'].ewm(span=12).mean()
            exp2 = data['Close'].ewm(span=26).mean()
            data['MACD'] = exp1 - exp2
            
            # Bollinger Bands
            data['BB_middle'] = data['Close'].rolling(window=20).mean()
            bb_std = data['Close'].rolling(window=20).std()
            data['BB_upper'] = data['BB_middle'] + (bb_std * 2)
            data['BB_lower'] = data['BB_middle'] - (bb_std * 2)
            
            # Volatility (20-day rolling)
            data['Volatility'] = data['Returns'].rolling(window=20).std() * np.sqrt(252)
            
            return data.dropna()
            
        except Exception as e:
            logger.error(f"Error generating mock data for {symbol}: {str(e)}")
            return None
    
    def get_stock_info(self, symbol: str) -> Optional[Dict]:
        """Get comprehensive stock information (mock data)"""
        try:
            # Generate mock stock information
            np.random.seed(hash(symbol) % 1000)  # Consistent data for each symbol
            
            # Base price calculation (same as in get_real_stock_data)
            base_price = 100 + (hash(symbol) % 200)
            
            # Mock company names
            company_names = {
                'AAPL': 'Apple Inc.',
                'MSFT': 'Microsoft Corporation',
                'GOOGL': 'Alphabet Inc.',
                'AMZN': 'Amazon.com Inc.',
                'TSLA': 'Tesla Inc.',
                'META': 'Meta Platforms Inc.',
                'NVDA': 'NVIDIA Corporation',
                'JPM': 'JPMorgan Chase & Co.',
                'JNJ': 'Johnson & Johnson',
                'V': 'Visa Inc.',
                'PG': 'Procter & Gamble Co.',
                'HD': 'Home Depot Inc.',
                'MA': 'Mastercard Inc.',
                'UNH': 'UnitedHealth Group Inc.',
                'DIS': 'Walt Disney Co.',
                'PYPL': 'PayPal Holdings Inc.',
                'ADBE': 'Adobe Inc.',
                'CRM': 'Salesforce Inc.',
                'NFLX': 'Netflix Inc.',
                'NKE': 'Nike Inc.',
                'KO': 'Coca-Cola Co.',
                'PEP': 'PepsiCo Inc.',
                'WMT': 'Walmart Inc.',
                'COST': 'Costco Wholesale Corp.',
                'BA': 'Boeing Co.',
                'CAT': 'Caterpillar Inc.',
                'XOM': 'Exxon Mobil Corp.',
                'CVX': 'Chevron Corp.'
            }
            
            # Mock sectors
            sectors = {
                'AAPL': 'Technology', 'MSFT': 'Technology', 'GOOGL': 'Technology', 'NVDA': 'Technology',
                'ADBE': 'Technology', 'CRM': 'Technology', 'AMZN': 'Consumer Cyclical', 'TSLA': 'Consumer Cyclical',
                'HD': 'Consumer Cyclical', 'NKE': 'Consumer Cyclical', 'META': 'Communication Services',
                'DIS': 'Communication Services', 'NFLX': 'Communication Services', 'JPM': 'Financial Services',
                'V': 'Financial Services', 'MA': 'Financial Services', 'PYPL': 'Financial Services',
                'JNJ': 'Healthcare', 'UNH': 'Healthcare', 'PG': 'Consumer Defensive', 'KO': 'Consumer Defensive',
                'PEP': 'Consumer Defensive', 'WMT': 'Consumer Defensive', 'COST': 'Consumer Defensive',
                'BA': 'Industrials', 'CAT': 'Industrials', 'XOM': 'Energy', 'CVX': 'Energy'
            }
            
            current_price = base_price * (1 + np.random.normal(0, 0.1))
            market_cap = current_price * (1000000000 + np.random.normal(0, 500000000))
            pe_ratio = 15 + np.random.normal(0, 10)
            beta = 0.8 + np.random.normal(0, 0.4)
            dividend_yield = np.random.uniform(0, 0.05)
            volume = 1000000 + np.random.normal(0, 500000)
            avg_volume = volume * (1 + np.random.normal(0, 0.3))
            
            return {
                'symbol': symbol,
                'name': company_names.get(symbol, f'{symbol} Corporation'),
                'current_price': current_price,
                'market_cap': market_cap,
                'pe_ratio': pe_ratio,
                'beta': beta,
                'sector': sectors.get(symbol, 'Technology'),
                'industry': sectors.get(symbol, 'Technology'),
                'dividend_yield': dividend_yield,
                'volume': volume,
                'avg_volume': avg_volume,
                'fifty_two_week_low': current_price * 0.7,
                'fifty_two_week_high': current_price * 1.3,
                'price_to_book': 2 + np.random.normal(0, 1),
                'debt_to_equity': 0.5 + np.random.normal(0, 0.3),
                'return_on_equity': 0.15 + np.random.normal(0, 0.1),
                'profit_margins': 0.1 + np.random.normal(0, 0.05)
            }
        except Exception as e:
            logger.error(f"Error getting stock info for {symbol}: {str(e)}")
            return None
    
    def calculate_risk_metrics(self, returns: pd.Series) -> Dict[str, float]:
        """Calculate comprehensive risk metrics"""
        if len(returns) < 30:
            return {}
        
        # Basic statistics
        mean_return = returns.mean() * 252  # Annualized
        volatility = returns.std() * np.sqrt(252)  # Annualized
        
        # Sharpe Ratio
        excess_returns = returns - (self.risk_free_rate / 252)
        sharpe_ratio = (excess_returns.mean() * 252) / volatility if volatility > 0 else 0
        
        # Maximum Drawdown
        cumulative_returns = (1 + returns).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        
        # Value at Risk (95% confidence)
        var_95 = np.percentile(returns, 5)
        
        # Expected Shortfall (Conditional VaR)
        es_95 = returns[returns <= var_95].mean()
        
        # Skewness and Kurtosis
        skewness = stats.skew(returns)
        kurtosis = stats.kurtosis(returns)
        
        # Beta (if market data available)
        beta = 1.0  # Default, will be calculated with market data
        
        return {
            'mean_return': mean_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'var_95': var_95,
            'expected_shortfall': es_95,
            'skewness': skewness,
            'kurtosis': kurtosis,
            'beta': beta
        }
    
    def calculate_portfolio_metrics(self, portfolio_data: List[Dict]) -> Dict[str, Any]:
        """Calculate portfolio-level metrics"""
        if not portfolio_data:
            return {}
        
        total_value = sum(item['value'] for item in portfolio_data)
        weights = [item['value'] / total_value for item in portfolio_data]
        
        # Get returns for all stocks
        all_returns = []
        stock_data = {}
        
        for item in portfolio_data:
            symbol = item['symbol']
            data = self.get_real_stock_data(symbol)
            if data is not None and 'Returns' in data.columns:
                stock_data[symbol] = data
                all_returns.append(data['Returns'])
        
        if not all_returns:
            return {}
        
        # Align returns by date
        returns_df = pd.concat(all_returns, axis=1, join='inner')
        returns_df.columns = [item['symbol'] for item in portfolio_data if item['symbol'] in stock_data]
        
        # Calculate portfolio returns
        portfolio_returns = (returns_df * weights).sum(axis=1)
        
        # Portfolio risk metrics
        portfolio_risk = self.calculate_risk_metrics(portfolio_returns)
        
        # Correlation matrix
        correlation_matrix = returns_df.corr()
        
        # Diversification metrics
        portfolio_variance = portfolio_returns.var() * 252
        weighted_individual_variance = sum(
            weights[i] ** 2 * returns_df.iloc[:, i].var() * 252 
            for i in range(len(weights))
        )
        diversification_ratio = weighted_individual_variance / portfolio_variance if portfolio_variance > 0 else 1
        
        # Sector allocation
        sector_allocation = {}
        for item in portfolio_data:
            info = self.get_stock_info(item['symbol'])
            if info and 'sector' in info:
                sector = info['sector']
                sector_allocation[sector] = sector_allocation.get(sector, 0) + item['value']
        
        # Risk assessment
        risk_assessment = self.assess_portfolio_risk(portfolio_risk, sector_allocation, correlation_matrix)
        
        return {
            'total_value': total_value,
            'weights': dict(zip([item['symbol'] for item in portfolio_data], weights)),
            'portfolio_risk': portfolio_risk,
            'correlation_matrix': correlation_matrix.to_dict(),
            'diversification_ratio': diversification_ratio,
            'sector_allocation': sector_allocation,
            'risk_assessment': risk_assessment,
            'stock_data': {
                symbol: {
                    'current_price': data['Close'].iloc[-1],
                    'volatility': data['Volatility'].iloc[-1] if 'Volatility' in data.columns else 0,
                    'rsi': data['RSI'].iloc[-1] if 'RSI' in data.columns else 50,
                    'beta': self.get_stock_info(symbol)['beta'] if self.get_stock_info(symbol) else 1.0
                } for symbol, data in stock_data.items()
            }
        }
    
    def assess_portfolio_risk(self, portfolio_risk: Dict, sector_allocation: Dict, correlation_matrix: pd.DataFrame) -> Dict[str, Any]:
        """Assess overall portfolio risk"""
        risk_score = 0
        risk_level = 'moderate'
        risk_factors = []
        
        # Volatility assessment
        volatility = portfolio_risk.get('volatility', 0)
        if volatility > 0.4:
            risk_score += 3
            risk_factors.append('High volatility (>40%)')
            risk_level = 'aggressive'
        elif volatility > 0.25:
            risk_score += 2
            risk_factors.append('Moderate-high volatility (25-40%)')
        elif volatility > 0.15:
            risk_score += 1
            risk_factors.append('Moderate volatility (15-25%)')
        else:
            risk_factors.append('Low volatility (<15%)')
        
        # Drawdown assessment
        max_drawdown = abs(portfolio_risk.get('max_drawdown', 0))
        if max_drawdown > 0.35:
            risk_score += 3
            risk_factors.append('Very high maximum drawdown (>35%)')
            risk_level = 'aggressive'
        elif max_drawdown > 0.20:
            risk_score += 2
            risk_factors.append('High maximum drawdown (20-35%)')
        elif max_drawdown > 0.10:
            risk_score += 1
            risk_factors.append('Moderate maximum drawdown (10-20%)')
        else:
            risk_factors.append('Low maximum drawdown (<10%)')
        
        # Sector concentration risk
        max_sector_weight = max(sector_allocation.values()) / sum(sector_allocation.values()) if sector_allocation else 0
        if max_sector_weight > 0.5:
            risk_score += 2
            risk_factors.append('High sector concentration (>50% in one sector)')
        elif max_sector_weight > 0.3:
            risk_score += 1
            risk_factors.append('Moderate sector concentration (30-50% in one sector)')
        else:
            risk_factors.append('Well-diversified across sectors')
        
        # Correlation risk
        avg_correlation = correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].mean()
        if avg_correlation > 0.7:
            risk_score += 2
            risk_factors.append('High correlation between holdings (>0.7)')
        elif avg_correlation > 0.5:
            risk_score += 1
            risk_factors.append('Moderate correlation between holdings (0.5-0.7)')
        else:
            risk_factors.append('Low correlation between holdings (<0.5)')
        
        # Sharpe ratio assessment
        sharpe_ratio = portfolio_risk.get('sharpe_ratio', 0)
        if sharpe_ratio > 1.0:
            risk_factors.append('Excellent risk-adjusted returns (Sharpe > 1.0)')
        elif sharpe_ratio > 0.5:
            risk_factors.append('Good risk-adjusted returns (Sharpe 0.5-1.0)')
        elif sharpe_ratio > 0:
            risk_factors.append('Positive risk-adjusted returns (Sharpe 0-0.5)')
        else:
            risk_score += 1
            risk_factors.append('Poor risk-adjusted returns (Sharpe < 0)')
        
        # Determine risk level based on score
        if risk_score >= 6:
            risk_level = 'aggressive'
        elif risk_score >= 3:
            risk_level = 'moderate'
        else:
            risk_level = 'conservative'
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'recommendations': self.generate_risk_recommendations(risk_factors, risk_level)
        }
    
    def generate_risk_recommendations(self, risk_factors: List[str], risk_level: str) -> List[str]:
        """Generate recommendations based on risk assessment"""
        recommendations = []
        
        if 'High volatility' in str(risk_factors):
            recommendations.append("Consider adding defensive stocks or bonds to reduce volatility")
        
        if 'High maximum drawdown' in str(risk_factors):
            recommendations.append("Implement stop-loss strategies to limit downside risk")
        
        if 'High sector concentration' in str(risk_factors):
            recommendations.append("Diversify across different sectors to reduce concentration risk")
        
        if 'High correlation' in str(risk_factors):
            recommendations.append("Add uncorrelated assets (bonds, commodities, international stocks)")
        
        if 'Poor risk-adjusted returns' in str(risk_factors):
            recommendations.append("Review portfolio allocation and consider rebalancing")
        
        if risk_level == 'aggressive':
            recommendations.append("Consider reducing position sizes or adding defensive assets")
        elif risk_level == 'conservative':
            recommendations.append("Portfolio appears well-balanced for conservative investors")
        
        return recommendations
    
    def get_portfolio_analysis(self, portfolio_data: List[Dict]) -> Dict[str, Any]:
        """Main method to get comprehensive portfolio analysis"""
        try:
            # Validate portfolio data
            if not portfolio_data:
                return {'error': 'No portfolio data provided'}
            
            # Calculate portfolio metrics
            portfolio_metrics = self.calculate_portfolio_metrics(portfolio_data)
            
            if not portfolio_metrics:
                return {'error': 'Unable to calculate portfolio metrics'}
            
            # Get individual stock analysis
            individual_analysis = []
            for item in portfolio_data:
                symbol = item['symbol']
                info = self.get_stock_info(symbol)
                data = self.get_real_stock_data(symbol)
                
                if info and data is not None:
                    stock_risk = self.calculate_risk_metrics(data['Returns'])
                    individual_analysis.append({
                        'symbol': symbol,
                        'info': info,
                        'risk_metrics': stock_risk,
                        'allocation': item['value'],
                        'weight': portfolio_metrics['weights'].get(symbol, 0)
                    })
            
            return {
                'portfolio_summary': {
                    'total_value': portfolio_metrics['total_value'],
                    'number_of_stocks': len(portfolio_data),
                    'risk_level': portfolio_metrics['risk_assessment']['risk_level'],
                    'risk_score': portfolio_metrics['risk_assessment']['risk_score']
                },
                'portfolio_metrics': portfolio_metrics,
                'individual_analysis': individual_analysis,
                'risk_assessment': portfolio_metrics['risk_assessment'],
                'sector_allocation': portfolio_metrics['sector_allocation'],
                'correlation_matrix': portfolio_metrics['correlation_matrix'],
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in portfolio analysis: {str(e)}")
            return {'error': f'Portfolio analysis failed: {str(e)}'}
    
    def get_stock_recommendations(self, portfolio_data: List[Dict], risk_tolerance: str = 'moderate') -> List[Dict]:
        """Get stock recommendations to improve portfolio"""
        try:
            current_symbols = {item['symbol'] for item in portfolio_data}
            current_sectors = set()
            
            # Get current sector allocation
            for item in portfolio_data:
                info = self.get_stock_info(item['symbol'])
                if info and 'sector' in info:
                    current_sectors.add(info['sector'])
            
            # Popular stocks by sector (you can expand this list)
            sector_stocks = {
                'Technology': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'ADBE', 'CRM'],
                'Healthcare': ['JNJ', 'PFE', 'UNH', 'ABBV', 'TMO', 'DHR', 'LLY', 'ABT'],
                'Financial Services': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'V', 'MA', 'AXP'],
                'Consumer Cyclical': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'SBUX', 'DIS'],
                'Consumer Defensive': ['PG', 'KO', 'PEP', 'WMT', 'COST', 'PM', 'MO'],
                'Industrials': ['BA', 'CAT', 'GE', 'MMM', 'HON', 'UPS', 'FDX'],
                'Energy': ['XOM', 'CVX', 'COP', 'EOG', 'SLB', 'KMI'],
                'Real Estate': ['SPG', 'PLD', 'AMT', 'CCI', 'EQIX', 'DLR'],
                'Communication Services': ['GOOGL', 'META', 'NFLX', 'DIS', 'CMCSA', 'VZ'],
                'Basic Materials': ['LIN', 'APD', 'FCX', 'NEM', 'DOW', 'DD']
            }
            
            recommendations = []
            
            # Recommend stocks from underrepresented sectors
            for sector, stocks in sector_stocks.items():
                if sector not in current_sectors:
                    for symbol in stocks[:3]:  # Top 3 from each sector
                        if symbol not in current_symbols:
                            info = self.get_stock_info(symbol)
                            if info:
                                recommendations.append({
                                    'symbol': symbol,
                                    'name': info['name'],
                                    'sector': sector,
                                    'reason': f'Diversification: Add {sector} exposure',
                                    'current_price': info['current_price'],
                                    'market_cap': info['market_cap'],
                                    'pe_ratio': info['pe_ratio']
                                })
            
            # Add some defensive stocks for risk management
            defensive_stocks = ['JNJ', 'PG', 'KO', 'WMT', 'COST', 'VZ', 'T']
            for symbol in defensive_stocks:
                if symbol not in current_symbols and len(recommendations) < 10:
                    info = self.get_stock_info(symbol)
                    if info:
                        recommendations.append({
                            'symbol': symbol,
                            'name': info['name'],
                            'sector': info['sector'],
                            'reason': 'Risk management: Defensive stock',
                            'current_price': info['current_price'],
                            'market_cap': info['market_cap'],
                            'pe_ratio': info['pe_ratio']
                        })
            
            return recommendations[:10]  # Return top 10 recommendations
            
        except Exception as e:
            logger.error(f"Error getting stock recommendations: {str(e)}")
            return [] 