#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import yfinance as yf
import requests
from typing import Dict, List, Optional, Tuple

YAHOO_SEARCH_URL = "https://query2.finance.yahoo.com/v1/finance/search"
YAHOO_USER_AGENT = "Mozilla/5.0"

# NSE trading symbols that differ on Yahoo Finance (NSE symbol -> Yahoo base symbol)
NSE_SYMBOL_ALIASES = {
    "ZOMATO": "ETERNAL",
    "ZOMATOLTD": "ETERNAL",
    "REC": "RECLTD",
    "TATAMOTORS": "TMCV",
    "TATAMTR": "TMCV",
}

# Display names for alias-only lookups (when user searches old/popular names)
ALIAS_COMPANY_NAMES = {
    "ETERNAL": "Eternal Ltd (Zomato)",
    "RECLTD": "REC Limited",
    "TMCV": "Tata Motors Limited",
}


def normalize_nse_ticker(symbol: str, default_exchange: str = "NS") -> str:
    """
    Normalize user input to a Yahoo Finance symbol (e.g. RELIANCE -> RELIANCE.NS).

    Handles extra .NS suffixes, applies known symbol renames, and preserves
    symbols with special characters (e.g. M&M).
    """
    if not symbol or not str(symbol).strip():
        raise ValueError("Ticker symbol is required")

    raw = str(symbol).strip().upper()
    exchange = default_exchange

    # Peel exchange suffix(es); user may type RELIANCE.NS or RELIANCE.NS.NS
    while True:
        if raw.endswith(".BO"):
            exchange = "BO"
            raw = raw[:-3]
            continue
        if raw.endswith(".NS"):
            exchange = "NS"
            raw = raw[:-3]
            continue
        break

    base = raw.strip()
    if not base:
        raise ValueError("Ticker symbol is required")

    base = NSE_SYMBOL_ALIASES.get(base, base)
    ticker = f"{base}.{exchange}"

    if _ticker_has_price_history(ticker):
        return ticker

    resolved = lookup_nse_yahoo_symbol(base, exchange)
    if resolved:
        return resolved

    return ticker


def _ticker_has_price_history(ticker: str) -> bool:
    """Return True if Yahoo returns recent OHLC data for the symbol."""
    hist = yf.Ticker(ticker).history(period="5d")
    if not hist.empty:
        return True
    hist = yf.Ticker(ticker).history(period="1mo")
    return not hist.empty


def lookup_nse_yahoo_symbol(base: str, exchange: str = "NS") -> Optional[str]:
    """
    Find the Yahoo Finance symbol when NSE code differs (e.g. REC -> RECLTD.NS).
    """
    queries = [f"{base}LTD", f"{base} LTD", base]

    for query in queries:
        for item in _yahoo_finance_search(query, count=15):
                symbol = item.get("symbol", "")
                if not symbol.endswith(f".{exchange}"):
                    continue
                if item.get("exchange") not in ("NSI", "NSE"):
                    continue
                if _ticker_has_price_history(symbol):
                    return symbol

    return None


def get_nse_display_symbol(yahoo_base: str) -> str:
    """Map Yahoo symbol base to familiar NSE ticker when they differ."""
    for nse_symbol, yahoo_symbol in NSE_SYMBOL_ALIASES.items():
        if yahoo_symbol == yahoo_base:
            return nse_symbol
    return yahoo_base


def _yahoo_finance_search(query: str, count: int = 20) -> List[dict]:
    """Query Yahoo Finance symbol search API."""
    try:
        response = requests.get(
            YAHOO_SEARCH_URL,
            params={"q": query, "quotesCount": count, "newsCount": 0},
            headers={"User-Agent": YAHOO_USER_AGENT},
            timeout=8,
        )
        if not response.ok:
            return []
        return response.json().get("quotes", [])
    except requests.RequestException:
        return []


def _alias_search_matches(text: str) -> List[Dict[str, str]]:
    """Suggest stocks when query matches a known NSE/Yahoo alias."""
    needle = text.strip().upper()
    if len(needle) < 2:
        return []

    matches = []
    for nse_symbol, yahoo_base in NSE_SYMBOL_ALIASES.items():
        company = ALIAS_COMPANY_NAMES.get(yahoo_base, yahoo_base)
        searchable = f"{nse_symbol} {yahoo_base} {company}".upper()
        if needle in searchable or nse_symbol.startswith(needle) or yahoo_base.startswith(needle):
            symbol = f"{yahoo_base}.NS"
            matches.append({
                "symbol": symbol,
                "ticker": nse_symbol,
                "name": company,
                "subtitle": f"NSE: {nse_symbol}",
            })
    return matches


def search_nse_stocks(query: str, limit: int = 8) -> List[Dict[str, str]]:
    """
    Search NSE-listed stocks by company name or ticker.

    Returns suggestions with company name and both NSE-style and Yahoo symbols.
    """
    text = query.strip()
    if len(text) < 2:
        return []

    seen = set()
    results: List[Dict[str, str]] = []

    for alias_hit in _alias_search_matches(text):
        if alias_hit["symbol"] not in seen:
            seen.add(alias_hit["symbol"])
            results.append(alias_hit)
            if len(results) >= limit:
                return results

    search_queries = (
        text,
        f"{text} NSE",
        f"{text} LTD",
        f"{text} LIMITED",
        f"{text}LTD",
    )

    for search_query in search_queries:
        for item in _yahoo_finance_search(search_query, count=25):
            symbol = item.get("symbol", "")
            if not symbol.endswith(".NS"):
                continue

            exchange = item.get("exchange", "")
            if exchange and exchange not in ("NSI", "NSE"):
                continue

            if symbol in seen:
                continue
            seen.add(symbol)

            yahoo_base = symbol.replace(".NS", "")
            nse_ticker = get_nse_display_symbol(yahoo_base)
            name = (
                item.get("shortname")
                or item.get("longname")
                or item.get("quoteType")
                or yahoo_base
            )

            results.append({
                "symbol": symbol,
                "ticker": nse_ticker,
                "name": name,
                "subtitle": f"NSE: {nse_ticker}",
            })

            if len(results) >= limit:
                return results

    return results


def validate_ticker_has_data(ticker: str) -> Tuple[bool, Optional[str]]:
    """
    Verify Yahoo Finance returns price history for the symbol.

    Returns:
        (True, None) if data exists, else (False, error_message).
    """
    if _ticker_has_price_history(ticker):
        return True, None

    base = ticker.split(".")[0]
    alias_hint = ""
    for nse_symbol, yahoo_base in NSE_SYMBOL_ALIASES.items():
        if base == yahoo_base:
            alias_hint = f" On NSE this stock is often listed as {nse_symbol}."
            break

    yahoo_hint = ""
    resolved = lookup_nse_yahoo_symbol(base, ticker.split(".")[-1] if "." in ticker else "NS")
    if resolved and resolved != ticker:
        yahoo_hint = f" Try '{resolved}' on Yahoo Finance instead."

    return (
        False,
        f"No data found for '{ticker}'{alias_hint}{yahoo_hint} "
        "Search your symbol at https://finance.yahoo.com/ (Indian stocks use .NS).",
    )


def to_percent(value: Optional[float]) -> Optional[float]:
    """Normalize ratio fields (0.18) and percent fields (18) to percent scale."""
    if value is None or pd.isna(value):
        return None
    if abs(value) <= 1:
        return value * 100
    return value


def format_number(value, decimals=2):
    """Format a number for display."""
    if pd.isna(value):
        return "N/A"
    if isinstance(value, (int, float)):
        return round(value, decimals)
    return value


def calculate_percentage(numerator, denominator, decimals=2):
    """Calculate percentage safely."""
    if denominator == 0 or pd.isna(denominator):
        return None
    return round((numerator / denominator) * 100, decimals)


def safe_division(numerator, denominator, default=None):
    """Perform safe division."""
    if denominator == 0 or pd.isna(denominator):
        return default
    if pd.isna(numerator):
        return default
    return numerator / denominator


def clean_financial_data(df):
    """Clean financial data by removing NaN and converting types."""
    if df is None or df.empty:
        return pd.DataFrame()
    
    # Remove rows with all NaN
    df = df.dropna(how='all')
    
    # Convert to numeric where possible
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col], errors='ignore')
        except:
            pass
    
    return df
