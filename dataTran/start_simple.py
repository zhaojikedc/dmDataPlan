#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
China Stock Market Prediction System - Simple Start Script
Simple startup script to avoid encoding issues
"""
import sys
import os
import time
from datetime import datetime

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import required modules
try:
    from stock_data_fetcher import StockDataFetcher
    from stock_analyzer import StockAnalyzer
    print("✓ All modules imported successfully")
except ImportError as e:
    print(f"✗ Failed to import modules: {e}")
    print("Please ensure all required files exist in the dataTran directory")
    sys.exit(1)

def main():
    """Main function - Simple startup demo"""
    try:
        print("=" * 60)
        print("China Stock Market Prediction System - Quick Start")
        print("=" * 60)
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Import necessary modules
        print("Importing modules...")
        print("✓ Modules imported successfully")
        print()
        
        # Create data fetcher
        print("Initializing data fetcher...")
        fetcher = StockDataFetcher()
        print("✓ Data fetcher initialized successfully")
        print()
        
        # Get stock list
        print("Fetching stock list...")
        stock_list = fetcher.get_stock_list()
        if stock_list.empty:
            print("✗ Failed to get stock list")
            return
        print(f"✓ Successfully fetched {len(stock_list)} stocks")
        print()
        
        # Show stock list preview
        print("Stock List Preview:")
        preview = stock_list.head(10)[['code', 'name', 'price', 'change_pct', 'market_cap']]
        print(preview.to_string(index=False))
        print()
        
        # User selects analysis mode
        print("Please select analysis mode:")
        print("1. Analyze single stock")
        print("2. Analyze hot stocks")
        print("3. Market sentiment analysis")
        print("4. Exit")
        print()
        
        while True:
            choice = input("Enter your choice (1-4): ").strip()
            
            if choice == '1':
                # Single stock analysis
                stock_code = input("Enter stock code (e.g., 000001): ").strip()
                if stock_code:
                    analyze_single_stock(stock_code)
                break
                
            elif choice == '2':
                # Hot stocks analysis
                analyze_hot_stocks(stock_list)
                break
                
            elif choice == '3':
                # Market sentiment analysis
                analyze_market_sentiment(stock_list)
                break
                
            elif choice == '4':
                print("Thank you for using!")
                break
                
            else:
                print("Invalid choice, please re-enter")
                print()
        
    except ImportError as e:
        print(f"✗ Module import failed: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install -r requirements.txt")
        
    except Exception as e:
        print(f"✗ System startup failed: {e}")
        print("Please check network connection and system configuration")

def analyze_single_stock(stock_code):
    """Analyze single stock"""
    print(f"\nAnalyzing stock: {stock_code}")
    print("-" * 40)
    
    try:
        # Create analyzer
        analyzer = StockAnalyzer()
        
        # Analyze stock
        print("Fetching historical data...")
        result = analyzer.analyze_stock(stock_code, days=365, prediction_days=5)
        
        if 'error' in result:
            print(f"✗ Analysis failed: {result['error']}")
            return
        
        # Show analysis results
        print("✓ Analysis completed!")
        print()
        print("Analysis Results:")
        print(f"  Stock Code: {result['stock_code']}")
        print(f"  Analysis Date: {result['analysis_date']}")
        print(f"  Data Period: {result['data_period']}")
        print(f"  Current Price: {result['current_price']:.2f}")
        print(f"  Price Change: {result['price_change_pct']:.2f}%")
        print(f"  Volume: {result['volume']:,.0f}")
        print()
        
        print("Technical Indicators:")
        tech = result['technical_indicators']
        print(f"  RSI: {tech['rsi']:.2f}")
        print(f"  MACD: {tech['macd']:.4f}")
        print(f"  Bollinger Band Position: {tech['bb_position']:.2f}")
        print(f"  MA Trend: {'Bullish' if tech['ma_trend'] == 'bullish' else 'Bearish'}")
        print()
        
        print("Trading Signals:")
        signals = result['trading_signals']
        signal_text = {1: 'Buy', 0: 'Hold', -1: 'Sell'}
        print(f"  Current Signal: {signal_text[signals['current_signal']]}")
        print(f"  Signal Strength: {signals['signal_strength']:.2f}")
        print()
        
        print("Risk Assessment:")
        risk = result['risk_assessment']
        risk_text = {'low': 'Low Risk', 'medium': 'Medium Risk', 'high': 'High Risk'}
        print(f"  Overall Risk: {risk_text[risk['overall_risk']]}")
        print(f"  Volatility Risk: {risk_text[risk['volatility_risk']]}")
        print(f"  RSI Risk: {risk_text[risk['rsi_risk']]}")
        print()
        
        print("Investment Recommendation:")
        print(f"  {result['recommendation']}")
        print()
        
        # Save analysis report
        filename = f"analysis_{stock_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        analyzer.save_analysis_report(result, filename)
        print(f"Analysis report saved: {filename}")
        
    except Exception as e:
        print(f"✗ Stock analysis failed: {e}")

def analyze_hot_stocks(stock_list):
    """Analyze hot stocks"""
    print("\nAnalyzing hot stocks...")
    print("-" * 40)
    
    try:
        # Select top 10 stocks by volume
        hot_stocks = stock_list.nlargest(10, 'volume')['code'].tolist()
        print(f"Selected top 10 stocks by volume: {hot_stocks}")
        print()
        
        # Create analyzer
        analyzer = StockAnalyzer()
        
        # Batch analysis
        print("Starting batch analysis...")
        results = analyzer.batch_analyze(hot_stocks, days=365, prediction_days=5)
        
        # Show results summary
        print("\nBatch analysis completed!")
        print()
        
        successful_results = [r for r in results if 'error' not in r]
        print(f"Successfully analyzed: {len(successful_results)} stocks")
        print(f"Analysis failed: {len(results) - len(successful_results)} stocks")
        print()
        
        if successful_results:
            print("Analysis Results Summary:")
            for result in successful_results:
                print(f"  {result['stock_code']}: {result['recommendation']} "
                      f"(Risk: {result['risk_assessment']['overall_risk']})")
            print()
            
            # Generate summary report
            summary = analyzer.generate_summary_report(results)
            print("Summary Report:")
            print(summary)
            
            # Save batch analysis report
            filename = f"batch_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            analyzer.save_batch_report(results, filename)
            print(f"\nBatch analysis report saved: {filename}")
        
    except Exception as e:
        print(f"✗ Batch analysis failed: {e}")

def analyze_market_sentiment(stock_list):
    """Analyze market sentiment"""
    print("\nAnalyzing market sentiment...")
    print("-" * 40)
    
    try:
        # Create analyzer
        analyzer = StockAnalyzer()
        
        # Analyze market sentiment
        sentiment = analyzer.analyze_market_sentiment(stock_list, top_n=100)
        
        if 'error' in sentiment:
            print(f"✗ Market sentiment analysis failed: {sentiment['error']}")
            return
        
        print("✓ Market sentiment analysis completed!")
        print()
        print("Market Sentiment Indicators:")
        print(f"  Total Stocks Analyzed: {sentiment['total_stocks']}")
        print(f"  Up Stocks: {sentiment['up_stocks']} ({sentiment['up_ratio']:.1%})")
        print(f"  Down Stocks: {sentiment['down_stocks']} ({sentiment['down_ratio']:.1%})")
        print(f"  Flat Stocks: {sentiment['flat_stocks']}")
        print(f"  Average Change: {sentiment['avg_change']:.2f}%")
        print(f"  Average Volume: {sentiment['avg_volume']:,.0f}")
        print()
        
        # Determine market sentiment
        sentiment_text = {
            'bullish': 'Bullish',
            'bearish': 'Bearish',
            'neutral': 'Neutral'
        }
        print(f"Market Sentiment: {sentiment_text[sentiment['sentiment']]}")
        
        # Get major index data
        print("\nFetching major index data...")
        from stock_data_fetcher import StockDataFetcher
        fetcher = StockDataFetcher()
        indices = fetcher.get_market_index()
        
        if not indices.empty:
            print("Major Indices:")
            for _, index in indices.iterrows():
                change_color = "🔴" if index['change_pct'] < 0 else "🟢"
                print(f"  {change_color} {index['name']}: {index['price']:.2f} "
                      f"({index['change_pct']:+.2f}%)")
        
    except Exception as e:
        print(f"✗ Market sentiment analysis failed: {e}")

if __name__ == "__main__":
    main()
