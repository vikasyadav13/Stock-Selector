#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from ..utils.helpers import format_number


class NewsSentimentAnalyzer:
    """Analyzes news sentiment for stocks."""
    
    def __init__(self, ticker: str):
        """
        Initialize the news sentiment analyzer.
        
        Args:
            ticker: Stock ticker symbol
        """
        self.ticker = ticker.upper()
        self.stock = yf.Ticker(self.ticker)
        self.vader_analyzer = SentimentIntensityAnalyzer()
        self._news = None
        
    def get_news(self) -> List[Dict]:
        """Get latest news for the stock."""
        if self._news is None:
            try:
                self._news = self.stock.news
            except Exception as e:
                print(f"Error fetching news for {self.ticker}: {e}")
                self._news = []
        return self._news if self._news else []

    def _extract_article_fields(self, article: Dict) -> Dict:
        """Normalize Yahoo news article shape (legacy and new API formats)."""
        content = article.get('content') or {}
        title = (
            article.get('title')
            or content.get('title')
            or ''
        )
        summary = (
            article.get('summary')
            or content.get('summary')
            or content.get('description')
            or ''
        )
        link = (
            article.get('link')
            or article.get('url')
            or (content.get('canonicalUrl') or {}).get('url')
            or (content.get('clickThroughUrl') or {}).get('url')
            or ''
        )
        published = (
            article.get('providerPublishTime')
            or content.get('pubDate')
            or article.get('pubDate')
            or ''
        )
        return {
            'title': title,
            'summary': summary,
            'link': link,
            'published': published,
        }

    def _classify_article(self, compound: float) -> str:
        if compound > 0.1:
            return 'positive'
        if compound < -0.1:
            return 'negative'
        return 'neutral'
    
    def analyze_sentiment_vader(self, text: str) -> Dict:
        """
        Analyze sentiment using VADER.
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary with sentiment scores
        """
        if not text:
            return {'compound': 0, 'positive': 0, 'negative': 0, 'neutral': 0}
        
        scores = self.vader_analyzer.polarity_scores(text)
        return {
            'compound': scores['compound'],
            'positive': scores['pos'],
            'negative': scores['neg'],
            'neutral': scores['neu']
        }
    
    def analyze_sentiment_textblob(self, text: str) -> Dict:
        """
        Analyze sentiment using TextBlob.
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary with sentiment scores
        """
        if not text:
            return {'polarity': 0, 'subjectivity': 0}
        
        blob = TextBlob(text)
        return {
            'polarity': blob.sentiment.polarity,
            'subjectivity': blob.sentiment.subjectivity
        }
    
    def analyze_news_sentiment(self) -> Dict:
        """
        Analyze sentiment of all news articles.
        
        Returns:
            Dictionary with sentiment analysis results
        """
        news_list = self.get_news()
        
        if not news_list:
            return {
                'total_articles': 0,
                'avg_vader_compound': 0,
                'avg_textblob_polarity': 0,
                'sentiment_label': 'Neutral',
                'recent_news': []
            }
        
        vader_scores = []
        textblob_scores = []
        recent_news = []
        good_news = []
        bad_news = []

        for article in news_list[:15]:
            fields = self._extract_article_fields(article)
            title = fields['title']
            summary = fields['summary']
            text = f"{title} {summary}"

            vader = self.analyze_sentiment_vader(text)
            textblob = self.analyze_sentiment_textblob(text)
            vader_scores.append(vader['compound'])
            textblob_scores.append(textblob['polarity'])

            item = {
                'title': title,
                'link': fields['link'],
                'published': fields['published'],
                'vader_score': vader['compound'],
                'textblob_score': textblob['polarity'],
                'sentiment': self._classify_article(vader['compound']),
            }
            recent_news.append(item)

            if item['sentiment'] == 'positive' and len(good_news) < 5:
                good_news.append(item)
            elif item['sentiment'] == 'negative' and len(bad_news) < 5:
                bad_news.append(item)
        
        # Calculate averages
        avg_vader = sum(vader_scores) / len(vader_scores) if vader_scores else 0
        avg_textblob = sum(textblob_scores) / len(textblob_scores) if textblob_scores else 0
        
        # Determine sentiment label
        sentiment_label = self._get_sentiment_label(avg_vader, avg_textblob)
        
        return {
            'total_articles': len(news_list),
            'avg_vader_compound': avg_vader,
            'avg_textblob_polarity': avg_textblob,
            'sentiment_label': sentiment_label,
            'recent_news': recent_news,
            'good_news': good_news,
            'bad_news': bad_news,
        }
    
    def _get_sentiment_label(self, vader_score: float, textblob_score: float) -> str:
        """
        Determine sentiment label based on scores.
        
        Args:
            vader_score: VADER compound score
            textblob_score: TextBlob polarity score
        
        Returns:
            Sentiment label (Positive, Negative, or Neutral)
        """
        # Combine both scores
        combined_score = (vader_score + textblob_score) / 2
        
        if combined_score > 0.1:
            return 'Positive'
        elif combined_score < -0.1:
            return 'Negative'
        else:
            return 'Neutral'
    
    def get_earnings_sentiment(self) -> Dict:
        """
        Analyze earnings-related news sentiment.
        
        Returns:
            Dictionary with earnings sentiment analysis
        """
        news_list = self.get_news()
        
        if not news_list:
            return {
                'earnings_news_count': 0,
                'earnings_sentiment': 'Neutral'
            }
        
        earnings_keywords = ['earnings', 'quarterly', 'q1', 'q2', 'q3', 'q4', 
                           'revenue', 'profit', 'eps', 'guidance']
        
        earnings_news = []
        for article in news_list:
            title = article.get('title', '').lower()
            summary = article.get('summary', '').lower()
            text = f"{title} {summary}"
            
            if any(keyword in text for keyword in earnings_keywords):
                earnings_news.append(article)
        
        if not earnings_news:
            return {
                'earnings_news_count': 0,
                'earnings_sentiment': 'Neutral'
            }
        
        # Analyze earnings news sentiment
        vader_scores = []
        for article in earnings_news:
            text = f"{article.get('title', '')} {article.get('summary', '')}"
            vader = self.analyze_sentiment_vader(text)
            vader_scores.append(vader['compound'])
        
        avg_earnings_sentiment = sum(vader_scores) / len(vader_scores) if vader_scores else 0
        
        if avg_earnings_sentiment > 0.1:
            sentiment = 'Positive'
        elif avg_earnings_sentiment < -0.1:
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'
        
        return {
            'earnings_news_count': len(earnings_news),
            'earnings_sentiment': sentiment,
            'avg_earnings_score': avg_earnings_sentiment
        }
    
    def analyze_sentiment(self) -> Dict:
        """
        Perform comprehensive sentiment analysis.
        
        Returns:
            Dictionary containing all sentiment metrics
        """
        news_sentiment = self.analyze_news_sentiment()
        earnings_sentiment = self.get_earnings_sentiment()
        
        analysis = {
            'ticker': self.ticker,
            'news_sentiment': news_sentiment,
            'earnings_sentiment': earnings_sentiment
        }
        
        # Calculate sentiment score
        analysis['sentiment_score'] = self._calculate_sentiment_score(analysis)
        
        return analysis
    
    def _calculate_sentiment_score(self, analysis: Dict) -> float:
        """
        Calculate a sentiment score (0-100) based on news sentiment.
        
        Scoring criteria:
        - Overall news sentiment: Positive is better
        - Earnings sentiment: Positive earnings news is good
        - Volume of news: More news indicates more interest
        """
        score = 0
        max_score = 100
        
        # Overall news sentiment (50 points)
        news_sentiment = analysis.get('news_sentiment', {})
        vader_score = news_sentiment.get('avg_vader_compound', 0)
        textblob_score = news_sentiment.get('avg_textblob_polarity', 0)
        sentiment_label = news_sentiment.get('sentiment_label', 'Neutral')
        
        if sentiment_label == 'Positive':
            score += 50
        elif sentiment_label == 'Neutral':
            score += 30
        else:  # Negative
            score += 10
        
        # Earnings sentiment (30 points)
        earnings_sentiment = analysis.get('earnings_sentiment', {})
        earnings_label = earnings_sentiment.get('earnings_sentiment', 'Neutral')
        
        if earnings_label == 'Positive':
            score += 30
        elif earnings_label == 'Neutral':
            score += 15
        else:  # Negative
            score += 5
        
        # News volume (20 points) - more news indicates more interest
        total_articles = news_sentiment.get('total_articles', 0)
        if total_articles >= 10:
            score += 20
        elif total_articles >= 5:
            score += 15
        elif total_articles >= 3:
            score += 10
        elif total_articles >= 1:
            score += 5
        
        return min(score, max_score)
    
    def get_sentiment_summary(self) -> str:
        """Get a human-readable summary of sentiment analysis."""
        analysis = self.analyze_sentiment()
        
        news_sentiment = analysis.get('news_sentiment', {})
        earnings_sentiment = analysis.get('earnings_sentiment', {})
        
        summary = f"""
News Sentiment Analysis for {self.ticker}
{'='*50}

Overall Sentiment:
- Total Articles: {news_sentiment.get('total_articles', 0)}
- VADER Compound Score: {format_number(news_sentiment.get('avg_vader_compound', 0), 3)}
- TextBlob Polarity: {format_number(news_sentiment.get('avg_textblob_polarity', 0), 3)}
- Sentiment Label: {news_sentiment.get('sentiment_label', 'Neutral')}

Earnings Sentiment:
- Earnings News Count: {earnings_sentiment.get('earnings_news_count', 0)}
- Earnings Sentiment: {earnings_sentiment.get('earnings_sentiment', 'Neutral')}
- Avg Earnings Score: {format_number(earnings_sentiment.get('avg_earnings_score', 0), 3)}

Sentiment Score: {format_number(analysis.get('sentiment_score', 0))}/100

Recent News Headlines:
"""
        for i, news in enumerate(news_sentiment.get('recent_news', [])[:5], 1):
            summary += f"{i}. {news.get('title', 'N/A')} (Score: {format_number(news.get('vader_score', 0), 3)})\n"
        
        return summary
