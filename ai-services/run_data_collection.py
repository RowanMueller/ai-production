#!/usr/bin/env python3
"""
Data Collection Script for AI Services
Run this to collect initial data for the enhanced chatbot
"""

import os
import sys
import logging
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_collector import DataCollector

def main():
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    logger.info("Starting data collection for enhanced chatbot...")
    
    # Initialize collector
    collector = DataCollector()
    
    # Define symbols to collect data for
    symbols = [
        'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 
        'NFLX', 'ADBE', 'CRM', 'ORCL', 'INTC', 'AMD', 'IBM', 
        'CSCO', 'QCOM', 'PYPL', 'V', 'MA', 'JPM', 'BAC', 'WMT', 'HD', 'DIS'
    ]
    
    logger.info(f"Collecting data for {len(symbols)} symbols...")
    
    try:
        # Collect all data
        collector.collect_all_data(symbols)
        
        logger.info("Data collection completed successfully!")
        logger.info("You can now use the enhanced chatbot with comprehensive data.")
        
        # Show what was collected
        data_dir = Path("data")
        if data_dir.exists():
            logger.info("\nCollected data summary:")
            for subdir in ['stocks', 'news', 'economic', 'prompts']:
                subdir_path = data_dir / subdir
                if subdir_path.exists():
                    files = list(subdir_path.glob("*.json"))
                    logger.info(f"  {subdir}: {len(files)} files")
        
    except Exception as e:
        logger.error(f"Error during data collection: {str(e)}")
        logger.error("Please check your API keys and internet connection.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 