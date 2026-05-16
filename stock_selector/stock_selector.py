#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
from typing import Dict, List, Optional, Union
from .fundamental_analysis.analyzer import FundamentalAnalyzer
from .technical_analysis.analyzer import TechnicalAnalyzer
from .news_sentiment.analyzer import NewsSentimentAnalyzer
from .utils.helpers import normalize_nse_ticker, validate_ticker_has_data


class StockSelector:
    """Main class for stock selection and analysis."""
    
    def __init__(self, ticker: str = None):
        """
        Initialize the stock selector.
        
        Args:
            ticker: Stock ticker symbol (optional, can be set later)
        """
        self.ticker = ticker.upper() if ticker else None
        self.fundamental_analyzer = None
        self.technical_analyzer = None
        self.sentiment_analyzer = None
        
        if self.ticker:
            self._initialize_analyzers()
    
    def _initialize_analyzers(self):
        """Initialize all analyzers for the current ticker."""
        if not self.ticker:
            return
        
        self.fundamental_analyzer = FundamentalAnalyzer(self.ticker)
        self.technical_analyzer = TechnicalAnalyzer(self.ticker)
        self.sentiment_analyzer = NewsSentimentAnalyzer(self.ticker)
    
    def set_ticker(self, ticker: str):
        """
        Set the ticker symbol.
        
        Args:
            ticker: Stock ticker symbol
        """
        self.ticker = normalize_nse_ticker(ticker)
        self._initialize_analyzers()
    
    def analyze_stock(self, ticker: str = None) -> Dict:
        """
        Perform comprehensive analysis of a stock.
        
        Args:
            ticker: Stock ticker symbol (optional if already set)
        
        Returns:
            Dictionary containing all analysis results
        """
        if ticker:
            self.set_ticker(normalize_nse_ticker(ticker))
        
        if not self.ticker:
            raise ValueError("Ticker symbol not set")

        valid, error_message = validate_ticker_has_data(self.ticker)
        if not valid:
            raise ValueError(error_message)
        
        # Perform all analyses
        fundamental_analysis = self.fundamental_analyzer.analyze_fundamentals()
        technical_analysis = self.technical_analyzer.analyze_technicals()
        sentiment_analysis = self.sentiment_analyzer.analyze_sentiment()
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(
            fundamental_analysis.get('fundamental_score', 0),
            technical_analysis.get('technical_score', 0),
            sentiment_analysis.get('sentiment_score', 0)
        )
        
        # Combine all analyses
        analysis = {
            'ticker': self.ticker,
            'fundamental': fundamental_analysis,
            'technical': technical_analysis,
            'sentiment': sentiment_analysis,
            'overall_score': overall_score,
            'recommendation': self._get_recommendation(overall_score)
        }
        
        return analysis
    
    def _calculate_overall_score(self, fundamental_score: float, 
                                 technical_score: float, 
                                 sentiment_score: float) -> float:
        """
        Calculate overall score (0-100) combining all analyses.
        
        Args:
            fundamental_score: Fundamental analysis score
            technical_score: Technical analysis score
            sentiment_score: Sentiment analysis score
        
        Returns:
            Overall score (0-100)
        """
        # Weight the different analyses
        # Fundamental: 40%, Technical: 35%, Sentiment: 25%
        weights = {
            'fundamental': 0.40,
            'technical': 0.35,
            'sentiment': 0.25
        }
        
        overall_score = (
            fundamental_score * weights['fundamental'] +
            technical_score * weights['technical'] +
            sentiment_score * weights['sentiment']
        )
        
        return round(overall_score, 2)
    
    def _get_recommendation(self, overall_score: float) -> str:
        """
        Get investment recommendation based on overall score.
        
        Args:
            overall_score: Overall analysis score (0-100)
        
        Returns:
            Recommendation string
        """
        if overall_score >= 80:
            return "Strong Buy"
        elif overall_score >= 70:
            return "Buy"
        elif overall_score >= 60:
            return "Moderate Buy"
        elif overall_score >= 50:
            return "Hold"
        elif overall_score >= 40:
            return "Moderate Sell"
        elif overall_score >= 30:
            return "Sell"
        else:
            return "Strong Sell"
    
    def analyze_multiple_stocks(self, tickers: List[str]) -> pd.DataFrame:
        """
        Analyze multiple stocks and return ranked results.
        
        Args:
            tickers: List of stock ticker symbols
        
        Returns:
            DataFrame with ranked analysis results
        """
        results = []
        
        for ticker in tickers:
            try:
                normalized = normalize_nse_ticker(ticker)
                analysis = self.analyze_stock(normalized)
                results.append({
                    'Ticker': normalized,
                    'Overall Score': analysis.get('overall_score', 0),
                    'Fundamental Score': analysis.get('fundamental', {}).get('fundamental_score', 0),
                    'Technical Score': analysis.get('technical', {}).get('technical_score', 0),
                    'Sentiment Score': analysis.get('sentiment', {}).get('sentiment_score', 0),
                    'Recommendation': analysis.get('recommendation', 'N/A'),
                    'Market Cap (M)': analysis.get('fundamental', {}).get('market_cap_millions', 0),
                    'P/E Ratio': analysis.get('fundamental', {}).get('pe_ratio', 0),
                    'RSI': analysis.get('technical', {}).get('rsi', 0),
                    'Price vs 200 SMA': 'Above' if analysis.get('technical', {}).get('price_vs_sma', {}).get('above_sma') else 'Below',
                    'News Sentiment': analysis.get('sentiment', {}).get('news_sentiment', {}).get('sentiment_label', 'N/A')
                })
            except ValueError as e:
                try:
                    normalized = normalize_nse_ticker(ticker)
                except ValueError:
                    normalized = str(ticker).upper()
                results.append({
                    'Ticker': normalized,
                    'Overall Score': 0,
                    'Fundamental Score': 0,
                    'Technical Score': 0,
                    'Sentiment Score': 0,
                    'Recommendation': str(e),
                    'Market Cap (M)': 0,
                    'P/E Ratio': 0,
                    'RSI': 0,
                    'Price vs 200 SMA': 'N/A',
                    'News Sentiment': 'N/A'
                })
            except Exception as e:
                print(f"Error analyzing {ticker}: {e}")
                try:
                    normalized = normalize_nse_ticker(ticker)
                except ValueError:
                    normalized = str(ticker).upper()
                results.append({
                    'Ticker': normalized,
                    'Overall Score': 0,
                    'Fundamental Score': 0,
                    'Technical Score': 0,
                    'Sentiment Score': 0,
                    'Recommendation': f'Error: {e}',
                    'Market Cap (M)': 0,
                    'P/E Ratio': 0,
                    'RSI': 0,
                    'Price vs 200 SMA': 'N/A',
                    'News Sentiment': 'N/A'
                })
        
        # Create DataFrame and sort by overall score
        df = pd.DataFrame(results)
        df = df.sort_values('Overall Score', ascending=False)
        df = df.reset_index(drop=True)
        
        return df
    
    def get_detailed_report(self, ticker: str = None) -> str:
        """
        Get a detailed analysis report for a stock.
        
        Args:
            ticker: Stock ticker symbol (optional if already set)
        
        Returns:
            Formatted report string
        """
        if ticker:
            self.set_ticker(ticker)
        
        analysis = self.analyze_stock()
        
        report = f"""
{'='*70}
                    STOCK ANALYSIS REPORT
{'='*70}

Ticker: {analysis['ticker']}
Recommendation: {analysis['recommendation']}
Overall Score: {analysis['overall_score']}/100

{'='*70}
                    FUNDAMENTAL ANALYSIS
{'='*70}
{self.fundamental_analyzer.get_fundamental_summary()}

{'='*70}
                    TECHNICAL ANALYSIS
{'='*70}
{self.technical_analyzer.get_technical_summary()}

{'='*70}
                    NEWS SENTIMENT ANALYSIS
{'='*70}
{self.sentiment_analyzer.get_sentiment_summary()}

{'='*70}
                    SUMMARY
{'='*70}
Fundamental Score: {analysis['fundamental']['fundamental_score']}/100
Technical Score: {analysis['technical']['technical_score']}/100
Sentiment Score: {analysis['sentiment']['sentiment_score']}/100
Overall Score: {analysis['overall_score']}/100
Recommendation: {analysis['recommendation']}

{'='*70}
"""
        return report
    
    def get_top_stocks(self, tickers: List[str], top_n: int = 10) -> pd.DataFrame:
        """
        Get top N stocks based on overall score.
        
        Args:
            tickers: List of stock ticker symbols
            top_n: Number of top stocks to return
        
        Returns:
            DataFrame with top N stocks
        """
        ranked_stocks = self.analyze_multiple_stocks(tickers)
        return ranked_stocks.head(top_n)
    
    def filter_stocks(self, tickers: List[str], 
                     min_fundamental_score: float = 50,
                     min_technical_score: float = 50,
                     min_sentiment_score: float = 50) -> pd.DataFrame:
        """
        Filter stocks based on minimum score criteria.
        
        Args:
            tickers: List of stock ticker symbols
            min_fundamental_score: Minimum fundamental score
            min_technical_score: Minimum technical score
            min_sentiment_score: Minimum sentiment score
        
        Returns:
            DataFrame with filtered stocks
        """
        ranked_stocks = self.analyze_multiple_stocks(tickers)
        
        filtered = ranked_stocks[
            (ranked_stocks['Fundamental Score'] >= min_fundamental_score) &
            (ranked_stocks['Technical Score'] >= min_technical_score) &
            (ranked_stocks['Sentiment Score'] >= min_sentiment_score)
        ]
        
        return filtered.reset_index(drop=True)
