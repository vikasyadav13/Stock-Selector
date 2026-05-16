#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from ..utils.helpers import format_number, calculate_percentage, safe_division


class TechnicalAnalyzer:
    """Analyzes technical indicators of stocks."""
    
    def __init__(self, ticker: str, period: str = "2y"):
        """
        Initialize the technical analyzer.
        
        Args:
            ticker: Stock ticker symbol
            period: Time period for analysis (default: 1y)
        """
        self.ticker = ticker.upper()
        self.period = period
        self.stock = yf.Ticker(self.ticker)
        self._history = None
        
    def get_history(self) -> pd.DataFrame:
        """Get historical price data."""
        if self._history is None:
            self._history = self.stock.history(period=self.period)
        return self._history
    
    def calculate_sma(self, period: int = 200) -> pd.Series:
        """
        Calculate Simple Moving Average.
        
        Args:
            period: SMA period (default: 200)
        
        Returns:
            Series with SMA values
        """
        history = self.get_history()
        if history.empty:
            return pd.Series()
        
        sma = history['Close'].rolling(window=period).mean()
        return sma
    
    def get_current_sma(self, period: int = 200) -> Optional[float]:
        """
        Get current SMA value.
        
        Args:
            period: SMA period (default: 200)
        
        Returns:
            Current SMA value
        """
        sma = self.calculate_sma(period)
        if sma.empty:
            return None
        return sma.iloc[-1]
    
    def calculate_rsi(self, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index.
        
        Args:
            period: RSI period (default: 14)
        
        Returns:
            Series with RSI values
        """
        history = self.get_history()
        if history.empty or len(history) < period + 1:
            return pd.Series()
        
        # Calculate price changes
        delta = history['Close'].diff()
        
        # Separate gains and losses
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # Calculate average gain and loss
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def get_current_rsi(self, period: int = 14) -> Optional[float]:
        """
        Get current RSI value.
        
        Args:
            period: RSI period (default: 14)
        
        Returns:
            Current RSI value
        """
        rsi = self.calculate_rsi(period)
        if rsi.empty:
            return None
        return rsi.iloc[-1]
    
    def get_52_week_high_low(self) -> Tuple[Optional[float], Optional[float]]:
        """
        Get 52-week high and low prices.
        
        Returns:
            Tuple of (52_week_high, 52_week_low)
        """
        history = self.get_history()
        if history.empty:
            return None, None
        
        # Get last 252 trading days (approximately 52 weeks)
        year_history = history.tail(252)
        
        if year_history.empty:
            return None, None
        
        high_52w = year_history['High'].max()
        low_52w = year_history['Low'].min()
        
        return high_52w, low_52w
    
    def get_distance_from_52_week_high(self) -> Optional[float]:
        """
        Calculate percentage distance from 52-week high.
        
        Returns:
            Percentage distance from 52-week high
        """
        history = self.get_history()
        if history.empty:
            return None
        
        high_52w, low_52w = self.get_52_week_high_low()
        current_price = history['Close'].iloc[-1]
        
        if high_52w is None or current_price is None:
            return None
        
        distance = calculate_percentage(high_52w - current_price, high_52w)
        return distance
    
    def get_distance_from_52_week_low(self) -> Optional[float]:
        """
        Calculate percentage distance from 52-week low.
        
        Returns:
            Percentage distance from 52-week low
        """
        history = self.get_history()
        if history.empty:
            return None
        
        high_52w, low_52w = self.get_52_week_high_low()
        current_price = history['Close'].iloc[-1]
        
        if low_52w is None or current_price is None:
            return None
        
        distance = calculate_percentage(current_price - low_52w, low_52w)
        return distance
    
    def get_volume_metrics(self) -> Dict:
        """Current and average volume metrics."""
        history = self.get_history()
        if history.empty or 'Volume' not in history.columns:
            return {
                'current_volume': None,
                'avg_volume_20d': None,
                'volume_ratio': None,
            }

        volumes = history['Volume'].dropna()
        if volumes.empty:
            return {
                'current_volume': None,
                'avg_volume_20d': None,
                'volume_ratio': None,
            }

        current_volume = float(volumes.iloc[-1])
        avg_volume = float(volumes.tail(20).mean())
        ratio = safe_division(current_volume, avg_volume)

        return {
            'current_volume': current_volume,
            'avg_volume_20d': avg_volume,
            'volume_ratio': ratio,
        }

    def get_chart_data(self, days: int = 180) -> Dict:
        """Price/volume series for charting (last N trading days)."""
        history = self.get_history()
        if history.empty:
            return {'dates': [], 'prices': [], 'volumes': []}

        subset = history.tail(days)
        return {
            'dates': [d.strftime('%Y-%m-%d') for d in subset.index],
            'prices': [round(float(v), 2) for v in subset['Close']],
            'volumes': [int(v) for v in subset['Volume'].fillna(0)],
        }

    def check_price_vs_sma(self, period: int = 200) -> Dict:
        """
        Check current price vs SMA.
        
        Args:
            period: SMA period (default: 200)
        
        Returns:
            Dictionary with comparison results
        """
        history = self.get_history()
        if history.empty:
            return {'above_sma': False, 'sma': None, 'current_price': None}
        
        current_price = history['Close'].iloc[-1]
        sma = self.get_current_sma(period)
        
        if sma is None:
            return {'above_sma': False, 'sma': None, 'current_price': current_price}
        
        above_sma = current_price > sma
        percentage_diff = calculate_percentage(current_price - sma, sma)
        
        return {
            'above_sma': above_sma,
            'sma': sma,
            'current_price': current_price,
            'percentage_diff': percentage_diff
        }
    
    def analyze_technicals(self) -> Dict:
        """
        Perform comprehensive technical analysis.
        
        Returns:
            Dictionary containing all technical metrics
        """
        price_vs_sma = self.check_price_vs_sma(200)
        volume = self.get_volume_metrics()

        analysis = {
            'ticker': self.ticker,
            'current_price': price_vs_sma.get('current_price'),
            'sma_200': self.get_current_sma(200),
            'rsi': self.get_current_rsi(14),
            '52_week_high': self.get_52_week_high_low()[0],
            '52_week_low': self.get_52_week_high_low()[1],
            'distance_from_52w_high': self.get_distance_from_52_week_high(),
            'distance_from_52w_low': self.get_distance_from_52_week_low(),
            'price_vs_sma': price_vs_sma,
            'volume': volume,
            'chart': self.get_chart_data(),
        }
        
        # Calculate technical score
        analysis['technical_score'] = self._calculate_technical_score(analysis)
        
        return analysis
    
    def _calculate_technical_score(self, analysis: Dict) -> float:
        """
        Calculate a technical score (0-100) based on key indicators.
        
        Scoring criteria:
        - Price above 200 SMA: Positive signal
        - RSI: Between 30-70 is neutral, below 30 is oversold (buy), above 70 is overbought (sell)
        - 52-week position: Closer to high is bullish but watch for overextension
        """
        score = 0

        # Volume vs 20-day average (15 points)
        volume = analysis.get('volume', {})
        vol_ratio = volume.get('volume_ratio')
        if vol_ratio is not None:
            if vol_ratio >= 1.5:
                score += 15
            elif vol_ratio >= 1.2:
                score += 12
            elif vol_ratio >= 0.8:
                score += 8
            else:
                score += 4

        # Price vs 200 SMA (25 points)
        price_vs_sma = analysis.get('price_vs_sma', {})
        if price_vs_sma.get('above_sma'):
            score += 25
        else:
            score += 8

        # RSI score (35 points)
        rsi = analysis.get('rsi')
        if rsi:
            if 30 <= rsi <= 70:
                score += 35
            elif rsi < 30:
                score += 30
            elif rsi < 40:
                score += 25
            elif rsi > 70:
                score += 8
            elif rsi > 60:
                score += 18

        # 52-week position (25 points)
        distance_high = analysis.get('distance_from_52_week_high')
        distance_low = analysis.get('distance_from_52_week_low')
        
        if distance_high is not None and distance_low is not None:
            # Prefer stocks not too close to 52-week high (avoid overbought)
            # But also not too close to 52-week low (avoid weak stocks)
            if distance_high > 10 and distance_low > 20:
                score += 25
            elif distance_high > 5 and distance_low > 10:
                score += 18
            elif distance_high < 5:
                score += 5
            elif distance_low < 10:
                score += 8
            else:
                score += 12
        
        return min(score, 100)
    
    def get_technical_summary(self) -> str:
        """Get a human-readable summary of technical analysis."""
        analysis = self.analyze_technicals()
        
        price_vs_sma = analysis.get('price_vs_sma', {})
        
        summary = f"""
Technical Analysis for {self.ticker}
{'='*50}

Key Indicators:
- 200-day SMA: ${format_number(analysis.get('sma_200', 0))}
- Current Price: ${format_number(price_vs_sma.get('current_price', 0))}
- Price vs 200 SMA: {'Above' if price_vs_sma.get('above_sma') else 'Below'} ({format_number(price_vs_sma.get('percentage_diff', 0))}%)
- RSI (14): {format_number(analysis.get('rsi', 0))}
- 52-week High: ${format_number(analysis.get('52_week_high', 0))}
- 52-week Low: ${format_number(analysis.get('52_week_low', 0))}
- Distance from 52w High: {format_number(analysis.get('distance_from_52w_high', 0))}%
- Distance from 52w Low: {format_number(analysis.get('distance_from_52w_low', 0))}%

Technical Score: {format_number(analysis.get('technical_score', 0))}/100

RSI Interpretation:
- RSI < 30: Oversold (Potential Buy)
- RSI 30-70: Neutral Zone
- RSI > 70: Overbought (Potential Sell)
"""
        return summary
