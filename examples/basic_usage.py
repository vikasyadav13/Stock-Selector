#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Example usage of the Stock Selector library.
"""

from stock_selector import StockSelector


def example_single_stock_analysis():
    """Analyze a single stock."""
    print("=" * 70)
    print("Example 1: Single Stock Analysis")
    print("=" * 70)
    
    selector = StockSelector()
    
    # Analyze Apple stock
    analysis = selector.analyze_stock('AAPL')
    
    print(f"\nTicker: {analysis['ticker']}")
    print(f"Overall Score: {analysis['overall_score']}/100")
    print(f"Recommendation: {analysis['recommendation']}")
    print(f"\nFundamental Score: {analysis['fundamental']['fundamental_score']}/100")
    print(f"Technical Score: {analysis['technical']['technical_score']}/100")
    print(f"Sentiment Score: {analysis['sentiment']['sentiment_score']}/100")


def example_detailed_report():
    """Generate a detailed report for a stock."""
    print("\n" + "=" * 70)
    print("Example 2: Detailed Report")
    print("=" * 70)
    
    selector = StockSelector()
    report = selector.get_detailed_report('AAPL')
    print(report)


def example_multiple_stocks():
    """Analyze multiple stocks and get rankings."""
    print("\n" + "=" * 70)
    print("Example 3: Multiple Stock Analysis")
    print("=" * 70)
    
    selector = StockSelector()
    
    # Analyze multiple stocks
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    ranked_stocks = selector.analyze_multiple_stocks(tickers)
    
    print(ranked_stocks.to_string(index=False))


def example_top_stocks():
    """Get top N stocks from a list."""
    print("\n" + "=" * 70)
    print("Example 4: Top Stocks")
    print("=" * 70)
    
    selector = StockSelector()
    
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'V', 'JNJ']
    top_stocks = selector.get_top_stocks(tickers, top_n=5)
    
    print(f"Top 5 Stocks:")
    print(top_stocks.to_string(index=False))


def example_filter_stocks():
    """Filter stocks based on criteria."""
    print("\n" + "=" * 70)
    print("Example 5: Filter Stocks")
    print("=" * 70)
    
    selector = StockSelector()
    
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA']
    filtered = selector.filter_stocks(
        tickers,
        min_fundamental_score=50,
        min_technical_score=50,
        min_sentiment_score=40
    )
    
    print(f"Filtered Stocks (Fundamental >= 50, Technical >= 50, Sentiment >= 40):")
    print(filtered.to_string(index=False))


def example_individual_analyzers():
    """Use individual analyzers separately."""
    print("\n" + "=" * 70)
    print("Example 6: Individual Analyzers")
    print("=" * 70)
    
    from stock_selector.fundamental_analysis import FundamentalAnalyzer
    from stock_selector.technical_analysis import TechnicalAnalyzer
    from stock_selector.news_sentiment import NewsSentimentAnalyzer
    
    # Fundamental analysis only
    fund_analyzer = FundamentalAnalyzer('AAPL')
    fund_summary = fund_analyzer.get_fundamental_summary()
    print(fund_summary)
    
    # Technical analysis only
    tech_analyzer = TechnicalAnalyzer('AAPL')
    tech_summary = tech_analyzer.get_technical_summary()
    print(tech_summary)
    
    # Sentiment analysis only
    sentiment_analyzer = NewsSentimentAnalyzer('AAPL')
    sentiment_summary = sentiment_analyzer.get_sentiment_summary()
    print(sentiment_summary)


if __name__ == '__main__':
    # Run all examples
    example_single_stock_analysis()
    example_detailed_report()
    example_multiple_stocks()
    example_top_stocks()
    example_filter_stocks()
    example_individual_analyzers()
