#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
from ..utils.helpers import (
    format_number,
    calculate_percentage,
    safe_division,
    clean_financial_data,
    to_percent,
)

REVENUE_KEYS = ['total revenue', 'revenue', 'net sales', 'sales']
PROFIT_KEYS = [
    'net income',
    'net income common stockholders',
    'net income applicable to common shares',
    'net profit',
]


class FundamentalAnalyzer:
    """Analyzes fundamental metrics of stocks."""

    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self.stock = yf.Ticker(self.ticker)
        self._info = None

    def get_info(self) -> Dict:
        if self._info is None:
            self._info = self.stock.info or {}
        return self._info

    def get_market_cap(self) -> Optional[float]:
        market_cap = self.get_info().get('marketCap')
        if market_cap is None:
            return None
        return market_cap / 1_000_000

    def get_ltp(self) -> Optional[float]:
        info = self.get_info()
        return info.get('currentPrice') or info.get('regularMarketPrice')

    def get_pe_ratio(self) -> Optional[float]:
        info = self.get_info()
        return info.get('trailingPE') or info.get('forwardPE')

    def get_eps(self) -> Optional[float]:
        info = self.get_info()
        return info.get('trailingEps') or info.get('forwardEps')

    def get_peg_ratio(self) -> Optional[float]:
        return self.get_info().get('pegRatio')

    def get_roce(self) -> Optional[float]:
        try:
            balance_sheet = self.stock.balance_sheet
            income_stmt = self.stock.income_stmt
            if balance_sheet is None or income_stmt is None or balance_sheet.empty:
                return None

            total_assets = balance_sheet.iloc[:, 0].get('Total Assets')
            current_liabilities = balance_sheet.iloc[:, 0].get('Total Current Liabilities')
            ebit = income_stmt.iloc[:, 0].get('EBIT')
            if ebit is None:
                ebit = income_stmt.iloc[:, 0].get('Operating Income')

            capital_employed = (total_assets or 0) - (current_liabilities or 0)
            if capital_employed and capital_employed != 0 and ebit is not None:
                return (ebit / capital_employed) * 100
            return None
        except Exception as e:
            print(f"Error calculating ROCE for {self.ticker}: {e}")
            return None

    def get_roe(self) -> Optional[float]:
        return to_percent(self.get_info().get('returnOnEquity'))

    def _find_financial_row(self, df: pd.DataFrame, keywords: List[str]) -> Optional[pd.Series]:
        if df is None or df.empty:
            return None
        for idx in df.index:
            label = str(idx).lower()
            if any(key in label for key in keywords):
                return df.loc[idx]
        return None

    def _period_growth(self, series: pd.Series, periods_apart: int) -> Optional[float]:
        if series is None or len(series) <= periods_apart:
            return None
        current = series.iloc[0]
        previous = series.iloc[periods_apart]
        if pd.isna(current) or pd.isna(previous) or previous == 0:
            return None
        return ((current - previous) / abs(previous)) * 100

    def get_financial_growth(self) -> Dict:
        """Quarterly and yearly sales/profit YoY growth (%)."""
        growth = {
            'quarterly_sales_growth': None,
            'quarterly_profit_growth': None,
            'yearly_sales_growth': None,
            'yearly_profit_growth': None,
        }

        try:
            q_income = self.stock.quarterly_income_stmt
            if q_income is not None and not q_income.empty:
                q_rev = self._find_financial_row(q_income, REVENUE_KEYS)
                q_profit = self._find_financial_row(q_income, PROFIT_KEYS)
                growth['quarterly_sales_growth'] = self._period_growth(q_rev, 4)
                growth['quarterly_profit_growth'] = self._period_growth(q_profit, 4)
        except Exception as e:
            print(f"Error quarterly growth for {self.ticker}: {e}")

        try:
            y_income = self.stock.income_stmt
            if y_income is not None and not y_income.empty:
                y_rev = self._find_financial_row(y_income, REVENUE_KEYS)
                y_profit = self._find_financial_row(y_income, PROFIT_KEYS)
                growth['yearly_sales_growth'] = self._period_growth(y_rev, 1)
                growth['yearly_profit_growth'] = self._period_growth(y_profit, 1)
        except Exception as e:
            print(f"Error yearly growth for {self.ticker}: {e}")

        return growth

    def get_promoter_holding(self) -> Optional[float]:
        """Insider/promoter holding % (best available from Yahoo)."""
        info = self.get_info()
        for key in ('heldPercentInsiders', 'insidersPercentHeld', 'promoterHolding'):
            val = info.get(key)
            if val is not None and not pd.isna(val):
                return to_percent(val)
        return None

    def get_quarterly_results(self) -> pd.DataFrame:
        try:
            return clean_financial_data(self.stock.quarterly_income_stmt)
        except Exception as e:
            print(f"Error getting quarterly results for {self.ticker}: {e}")
            return pd.DataFrame()

    def get_profit_loss(self) -> pd.DataFrame:
        try:
            return clean_financial_data(self.stock.income_stmt)
        except Exception as e:
            print(f"Error getting P&L for {self.ticker}: {e}")
            return pd.DataFrame()

    def get_balance_sheet(self) -> pd.DataFrame:
        try:
            return clean_financial_data(self.stock.balance_sheet)
        except Exception as e:
            print(f"Error getting balance sheet for {self.ticker}: {e}")
            return pd.DataFrame()

    def get_shareholding_pattern(self) -> Dict:
        try:
            holders = self.stock.institutional_holders
            major = self.stock.major_holders
            return {
                'institutional_holders': holders if holders is not None else pd.DataFrame(),
                'major_holders': major if major is not None else pd.DataFrame(),
                'promoter_holding_pct': self.get_promoter_holding(),
            }
        except Exception as e:
            print(f"Error getting shareholding pattern for {self.ticker}: {e}")
            return {}

    def analyze_fundamentals(self) -> Dict:
        growth = self.get_financial_growth()
        roce = self.get_roce()
        roe = self.get_roe()

        analysis = {
            'ticker': self.ticker,
            'current_price': self.get_ltp(),
            'market_cap_millions': self.get_market_cap(),
            'ltp': self.get_ltp(),
            'pe_ratio': self.get_pe_ratio(),
            'eps': self.get_eps(),
            'peg_ratio': self.get_peg_ratio(),
            'roce': roce,
            'roe': roe,
            'promoter_holding': self.get_promoter_holding(),
            'financial_growth': growth,
            'quarterly_results': self.get_quarterly_results(),
            'profit_loss': self.get_profit_loss(),
            'balance_sheet': self.get_balance_sheet(),
            'shareholding_pattern': self.get_shareholding_pattern(),
        }
        analysis['fundamental_score'] = self._calculate_fundamental_score(analysis)
        return analysis

    def _score_growth(self, growth_pct: Optional[float], max_points: float = 10) -> float:
        if growth_pct is None:
            return 0
        if growth_pct >= 20:
            return max_points
        if growth_pct >= 10:
            return max_points * 0.7
        if growth_pct > 0:
            return max_points * 0.4
        return 0

    def _score_eps_vs_pe(self, eps: Optional[float], pe: Optional[float]) -> float:
        """Higher score when EPS exceeds P/E (value/earnings strength signal)."""
        if eps is None or pe is None or pe <= 0:
            return 0
        if eps > pe:
            return 10
        ratio = eps / pe
        if ratio >= 0.8:
            return 7
        if ratio >= 0.5:
            return 4
        return 2

    def _score_peg(self, peg: Optional[float]) -> float:
        if peg is None:
            return 0
        if peg <= 0 or peg > 2:
            return 0
        if peg <= 1:
            return 15
        if peg <= 1.5:
            return 12
        return 8

    def _score_roe_roce(self, value: Optional[float]) -> float:
        pct = to_percent(value) if value is not None else None
        if pct is None:
            return 0
        if pct >= 20:
            return 12.5
        if pct >= 15:
            return 10
        if pct >= 10:
            return 6
        if pct >= 5:
            return 3
        return 0

    def _score_promoter(self, holding: Optional[float]) -> float:
        if holding is None:
            return 0
        if holding >= 50:
            return 10
        if holding >= 40:
            return 8
        if holding >= 30:
            return 6
        if holding >= 20:
            return 4
        return 2

    def _calculate_fundamental_score(self, analysis: Dict) -> float:
        score = 0
        growth = analysis.get('financial_growth', {})

        score += self._score_eps_vs_pe(analysis.get('eps'), analysis.get('pe_ratio'))
        score += self._score_growth(growth.get('quarterly_sales_growth'))
        score += self._score_growth(growth.get('quarterly_profit_growth'))
        score += self._score_growth(growth.get('yearly_sales_growth'))
        score += self._score_growth(growth.get('yearly_profit_growth'))
        score += self._score_promoter(analysis.get('promoter_holding'))
        score += self._score_peg(analysis.get('peg_ratio'))
        score += self._score_roe_roce(analysis.get('roe'))
        score += self._score_roe_roce(analysis.get('roce'))

        return min(round(score, 2), 100)

    def get_fundamental_summary(self) -> str:
        analysis = self.analyze_fundamentals()
        g = analysis.get('financial_growth', {})
        summary = f"""
Fundamental Analysis for {self.ticker}
{'='*50}

Key Metrics:
- Current Price: ₹{format_number(analysis.get('current_price', 0))}
- Market Cap: ₹{format_number(analysis.get('market_cap_millions', 0))}M
- P/E Ratio: {format_number(analysis.get('pe_ratio', 0))}
- EPS: ₹{format_number(analysis.get('eps', 0))}
- PEG Ratio: {format_number(analysis.get('peg_ratio', 0))}
- ROE: {format_number(analysis.get('roe', 0))}%
- ROCE: {format_number(analysis.get('roce', 0))}%
- Promoter/Insider Holding: {format_number(analysis.get('promoter_holding', 0))}%

Growth (YoY %):
- Quarterly Sales: {format_number(g.get('quarterly_sales_growth', 0))}%
- Quarterly Profit: {format_number(g.get('quarterly_profit_growth', 0))}%
- Yearly Sales: {format_number(g.get('yearly_sales_growth', 0))}%
- Yearly Profit: {format_number(g.get('yearly_profit_growth', 0))}%

Fundamental Score: {format_number(analysis.get('fundamental_score', 0))}/100
"""
        return summary
