#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys
from .stock_selector import StockSelector
from .utils.helpers import normalize_nse_ticker


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Stock Selector - Analyze stocks using fundamental and technical analysis'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze single stock
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a single stock')
    analyze_parser.add_argument('ticker', help='Stock ticker symbol')
    analyze_parser.add_argument('--report', action='store_true', 
                               help='Generate detailed report')
    
    # Analyze multiple stocks
    multi_parser = subparsers.add_parser('multi', help='Analyze multiple stocks')
    multi_parser.add_argument('tickers', nargs='+', help='Stock ticker symbols')
    multi_parser.add_argument('--top', type=int, default=10,
                            help='Number of top stocks to show')
    multi_parser.add_argument('--output', choices=['console', 'csv'],
                            default='console', help='Output format')
    
    # Filter stocks
    filter_parser = subparsers.add_parser('filter', help='Filter stocks by criteria')
    filter_parser.add_argument('tickers', nargs='+', help='Stock ticker symbols')
    filter_parser.add_argument('--min-fundamental', type=float, default=50,
                              help='Minimum fundamental score')
    filter_parser.add_argument('--min-technical', type=float, default=50,
                              help='Minimum technical score')
    filter_parser.add_argument('--min-sentiment', type=float, default=50,
                              help='Minimum sentiment score')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    selector = StockSelector()
    
    if args.command == 'analyze':
        ticker = normalize_nse_ticker(args.ticker)
        
        if args.report:
            report = selector.get_detailed_report(ticker)
            print(report)
        else:
            analysis = selector.analyze_stock(ticker)
            print(f"\nStock Analysis for {ticker}")
            print(f"{'='*50}")
            print(f"Overall Score: {analysis['overall_score']}/100")
            print(f"Recommendation: {analysis['recommendation']}")
            print(f"\nFundamental Score: {analysis['fundamental']['fundamental_score']}/100")
            print(f"Technical Score: {analysis['technical']['technical_score']}/100")
            print(f"Sentiment Score: {analysis['sentiment']['sentiment_score']}/100")
    
    elif args.command == 'multi':
        tickers = [normalize_nse_ticker(t) for t in args.tickers]
        
        if args.output == 'console':
            top_stocks = selector.get_top_stocks(tickers, args.top)
            print(f"\nTop {args.top} Stocks")
            print(f"{'='*100}")
            print(top_stocks.to_string(index=False))
        elif args.output == 'csv':
            ranked_stocks = selector.analyze_multiple_stocks(tickers)
            ranked_stocks.to_csv('stock_analysis.csv', index=False)
            print(f"Results saved to stock_analysis.csv")
    
    elif args.command == 'filter':
        tickers = [normalize_nse_ticker(t) for t in args.tickers]
        
        filtered = selector.filter_stocks(
            tickers,
            min_fundamental_score=args.min_fundamental,
            min_technical_score=args.min_technical,
            min_sentiment_score=args.min_sentiment
        )
        print(f"\nFiltered Stocks")
        print(f"{'='*100}")
        print(filtered.to_string(index=False))


if __name__ == '__main__':
    main()
