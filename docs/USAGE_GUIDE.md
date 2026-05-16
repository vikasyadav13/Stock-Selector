# Stock Selector - Usage Guide

## Table of Contents
1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Python API Usage](#python-api-usage)
4. [Command Line Interface](#command-line-interface)
5. [Individual Analyzers](#individual-analyzers)
6. [Understanding Scores](#understanding-scores)
7. [Examples](#examples)
8. [Troubleshooting](#troubleshooting)

---

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Install Dependencies

```bash
cd /Users/admin/Documents/Learn_Backend/stock_selector
pip install -r requirements.txt
```

### Verify Installation

```bash
python -c "from stock_selector import StockSelector; print('Installation successful')"
```

---

## Quick Start

### Analyze a Single Stock

```python
from stock_selector import StockSelector

# Initialize selector
selector = StockSelector()

# Analyze Apple stock
analysis = selector.analyze_stock('AAPL')

# Print results
print(f"Overall Score: {analysis['overall_score']}/100")
print(f"Recommendation: {analysis['recommendation']}")
```

### Generate Detailed Report

```python
from stock_selector import StockSelector

selector = StockSelector()
report = selector.get_detailed_report('AAPL')
print(report)
```

---

## Python API Usage

### 1. Basic Stock Analysis

```python
from stock_selector import StockSelector

selector = StockSelector()

# Analyze a stock
analysis = selector.analyze_stock('AAPL')

# Access individual scores
fundamental_score = analysis['fundamental']['fundamental_score']
technical_score = analysis['technical']['technical_score']
sentiment_score = analysis['sentiment']['sentiment_score']
overall_score = analysis['overall_score']
recommendation = analysis['recommendation']

print(f"Fundamental: {fundamental_score}/100")
print(f"Technical: {technical_score}/100")
print(f"Sentiment: {sentiment_score}/100")
print(f"Overall: {overall_score}/100")
print(f"Recommendation: {recommendation}")
```

### 2. Access Fundamental Metrics

```python
from stock_selector import StockSelector

selector = StockSelector()
analysis = selector.analyze_stock('AAPL')

fundamental = analysis['fundamental']

# Key metrics
market_cap = fundamental['market_cap_millions']
pe_ratio = fundamental['pe_ratio']
eps = fundamental['eps']
peg_ratio = fundamental['peg_ratio']
roe = fundamental['roe']
roce = fundamental['roce']

print(f"Market Cap: ${market_cap}M")
print(f"P/E Ratio: {pe_ratio}")
print(f"EPS: ${eps}")
print(f"PEG Ratio: {peg_ratio}")
print(f"ROE: {roe}%")
print(f"ROCE: {roce}%")
```

### 3. Access Technical Indicators

```python
from stock_selector import StockSelector

selector = StockSelector()
analysis = selector.analyze_stock('AAPL')

technical = analysis['technical']

# Key indicators
sma_200 = technical['sma_200']
rsi = technical['rsi']
high_52w = technical['52_week_high']
low_52w = technical['52_week_low']
price_vs_sma = technical['price_vs_sma']

print(f"200-day SMA: ${sma_200}")
print(f"RSI: {rsi}")
print(f"52-week High: ${high_52w}")
print(f"52-week Low: ${low_52w}")
print(f"Price vs 200 SMA: {'Above' if price_vs_sma['above_sma'] else 'Below'}")
```

### 4. Access News Sentiment

```python
from stock_selector import StockSelector

selector = StockSelector()
analysis = selector.analyze_stock('AAPL')

sentiment = analysis['sentiment']['news_sentiment']

# Sentiment data
total_articles = sentiment['total_articles']
vader_score = sentiment['avg_vader_compound']
textblob_score = sentiment['avg_textblob_polarity']
sentiment_label = sentiment['sentiment_label']

print(f"Total Articles: {total_articles}")
print(f"VADER Score: {vader_score}")
print(f"TextBlob Score: {textblob_score}")
print(f"Sentiment: {sentiment_label}")
```

### 5. Analyze Multiple Stocks

```python
from stock_selector import StockSelector

selector = StockSelector()

# List of tickers
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

# Analyze all stocks
ranked_stocks = selector.analyze_multiple_stocks(tickers)

# Display results
print(ranked_stocks)
```

### 6. Get Top N Stocks

```python
from stock_selector import StockSelector

selector = StockSelector()

tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'V', 'JNJ']

# Get top 5 stocks
top_stocks = selector.get_top_stocks(tickers, top_n=5)
print(top_stocks)
```

### 7. Filter Stocks by Criteria

```python
from stock_selector import StockSelector

selector = StockSelector()

tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA']

# Filter stocks with minimum scores
filtered = selector.filter_stocks(
    tickers,
    min_fundamental_score=50,
    min_technical_score=50,
    min_sentiment_score=40
)

print(filtered)
```

### 8. Set Ticker After Initialization

```python
from stock_selector import StockSelector

# Initialize without ticker
selector = StockSelector()

# Set ticker later
selector.set_ticker('AAPL')

# Analyze
analysis = selector.analyze_stock()
```

---

## Command Line Interface

### Analyze Single Stock

```bash
python -m stock_selector analyze AAPL
```

### Generate Detailed Report

```bash
python -m stock_selector analyze AAPL --report
```

### Analyze Multiple Stocks

```bash
python -m stock_selector multi AAPL MSFT GOOGL AMZN TSLA
```

### Get Top N Stocks

```bash
python -m stock_selector multi AAPL MSFT GOOGL AMZN TSLA --top 5
```

### Export Results to CSV

```bash
python -m stock_selector multi AAPL MSFT GOOGL --output csv
```

This will create a file `stock_analysis.csv` in the current directory.

### Filter Stocks by Criteria

```bash
python -m stock_selector filter AAPL MSFT GOOGL --min-fundamental 50 --min-technical 50 --min-sentiment 40
```

### CLI Help

```bash
python -m stock_selector --help
python -m stock_selector analyze --help
python -m stock_selector multi --help
python -m stock_selector filter --help
```

---

## Individual Analyzers

### Fundamental Analyzer Only

```python
from stock_selector.fundamental_analysis import FundamentalAnalyzer

analyzer = FundamentalAnalyzer('AAPL')

# Get fundamental analysis
analysis = analyzer.analyze_fundamentals()

# Get summary
summary = analyzer.get_fundamental_summary()
print(summary)

# Access specific metrics
market_cap = analyzer.get_market_cap()
pe_ratio = analyzer.get_pe_ratio()
eps = analyzer.get_eps()
```

### Technical Analyzer Only

```python
from stock_selector.technical_analysis import TechnicalAnalyzer

analyzer = TechnicalAnalyzer('AAPL', period='1y')

# Get technical analysis
analysis = analyzer.analyze_technicals()

# Get summary
summary = analyzer.get_technical_summary()
print(summary)

# Access specific indicators
sma_200 = analyzer.get_current_sma(200)
rsi = analyzer.get_current_rsi(14)
high_52w, low_52w = analyzer.get_52_week_high_low()
```

### News Sentiment Analyzer Only

```python
from stock_selector.news_sentiment import NewsSentimentAnalyzer

analyzer = NewsSentimentAnalyzer('AAPL')

# Get sentiment analysis
analysis = analyzer.analyze_sentiment()

# Get summary
summary = analyzer.get_sentiment_summary()
print(summary)

# Access specific data
news_sentiment = analyzer.analyze_news_sentiment()
earnings_sentiment = analyzer.get_earnings_sentiment()
```

---

## Understanding Scores

### Fundamental Score (0-100)

**Components:**
- P/E Ratio (20 points): Lower is better
  - <15: 20 points
  - <25: 15 points
  - <40: 10 points
  - <60: 5 points

- PEG Ratio (20 points): Lower is better
  - <1.0: 20 points
  - <1.5: 15 points
  - <2.0: 10 points
  - <3.0: 5 points

- ROE (20 points): Higher is better
  - >20%: 20 points
  - >15%: 15 points
  - >10%: 10 points
  - >5%: 5 points

- ROCE (20 points): Higher is better
  - >20%: 20 points
  - >15%: 15 points
  - >10%: 10 points
  - >5%: 5 points

- Market Cap (20 points): Mid-cap preferred
  - >$10B (Large cap): 15 points
  - >$2B (Mid cap): 20 points
  - >$500M (Small cap): 10 points
  - <$500M (Micro cap): 5 points

### Technical Score (0-100)

**Components:**
- Price vs 200 SMA (30 points)
  - Above SMA: 30 points
  - Below SMA: 10 points

- RSI (40 points)
  - 30-70 (Neutral): 40 points
  - <30 (Oversold): 35 points
  - <40 (Slightly oversold): 30 points
  - >70 (Overbought): 10 points
  - >60 (Slightly overbought): 20 points

- 52-week Position (30 points)
  - Balanced (not too close to high/low): 30 points
  - Reasonable position: 20 points
  - Too close to 52-week high: 5 points
  - Too close to 52-week low: 10 points

### Sentiment Score (0-100)

**Components:**
- Overall Sentiment (50 points)
  - Positive: 50 points
  - Neutral: 30 points
  - Negative: 10 points

- Earnings Sentiment (30 points)
  - Positive: 30 points
  - Neutral: 15 points
  - Negative: 5 points

- News Volume (20 points)
  - >=10 articles: 20 points
  - >=5 articles: 15 points
  - >=3 articles: 10 points
  - >=1 article: 5 points

### Overall Score (0-100)

**Weighted Combination:**
- Fundamental: 40%
- Technical: 35%
- Sentiment: 25%

### Investment Recommendations

- **80-100**: Strong Buy
- **70-79**: Buy
- **60-69**: Moderate Buy
- **50-59**: Hold
- **40-49**: Moderate Sell
- **30-39**: Sell
- **0-29**: Strong Sell

---

## Examples

### Example 1: Quick Stock Check

```python
from stock_selector import StockSelector

selector = StockSelector()
analysis = selector.analyze_stock('AAPL')

print(f"AAPL Score: {analysis['overall_score']}/100")
print(f"Recommendation: {analysis['recommendation']}")
```

### Example 2: Compare Multiple Stocks

```python
from stock_selector import StockSelector

selector = StockSelector()

tech_stocks = ['AAPL', 'MSFT', 'GOOGL', 'META', 'NVDA']
results = selector.analyze_multiple_stocks(tech_stocks)

# Sort by overall score
results = results.sort_values('Overall Score', ascending=False)
print(results[['Ticker', 'Overall Score', 'Recommendation']])
```

### Example 3: Find Value Stocks

```python
from stock_selector import StockSelector

selector = StockSelector()

stocks = ['AAPL', 'MSFT', 'GOOGL', 'JPM', 'JNJ', 'PG']

# Filter for good fundamentals
value_stocks = selector.filter_stocks(
    stocks,
    min_fundamental_score=60,
    min_technical_score=40,
    min_sentiment_score=30
)

print(value_stocks)
```

### Example 4: Detailed Analysis Report

```python
from stock_selector import StockSelector

selector = StockSelector()

# Generate comprehensive report
report = selector.get_detailed_report('AAPL')

# Save to file
with open('AAPL_analysis.txt', 'w') as f:
    f.write(report)

print("Report saved to AAPL_analysis.txt")
```

### Example 5: Batch Analysis with CSV Export

```python
from stock_selector import StockSelector
import pandas as pd

selector = StockSelector()

# Large list of stocks
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 
           'JPM', 'V', 'JNJ', 'PG', 'KO', 'DIS', 'NFLX', 'AMD']

# Analyze all
results = selector.analyze_multiple_stocks(tickers)

# Export to CSV
results.to_csv('stock_analysis_results.csv', index=False)
print("Results exported to stock_analysis_results.csv")
```

---

## Troubleshooting

### Import Error: Module Not Found

**Problem:** `ModuleNotFoundError: No module named 'stock_selector'`

**Solution:**
```bash
# Make sure you're in the correct directory
cd /Users/admin/Documents/Learn_Backend/stock_selector

# Install dependencies
pip install -r requirements.txt

# Try importing again
python -c "from stock_selector import StockSelector"
```

### Missing Dependencies

**Problem:** Various import errors for missing packages

**Solution:**
```bash
pip install -r requirements.txt
```

### Data Fetching Errors

**Problem:** `yfinance` errors when fetching data

**Solution:**
- Check your internet connection
- Verify the ticker symbol is correct
- Yahoo Finance may be temporarily down
- Try again after a few minutes

### Empty Data Results

**Problem:** Analysis returns empty DataFrames or None values

**Solution:**
- The ticker may be delisted or invalid
- Check if the ticker exists on Yahoo Finance
- Try a different ticker symbol

### Rate Limiting

**Problem:** Too many requests to Yahoo Finance

**Solution:**
- Add delays between requests
- Use caching (yfinance has built-in caching)
- Reduce the number of stocks analyzed at once

### Sentiment Analysis Issues

**Problem:** Sentiment analysis returns neutral or errors

**Solution:**
- Some stocks may not have recent news
- Check if news data is available
- VADER and TextBlob require text to analyze

---

## Best Practices

1. **Start Small**: Test with a few stocks before analyzing large lists
2. **Use Caching**: yfinance has built-in caching to avoid rate limits
3. **Handle Errors**: Always wrap analysis in try-except blocks
4. **Validate Results**: Cross-check scores with other sources
5. **Regular Updates**: Financial data changes frequently
6. **Combine Metrics**: Don't rely on a single metric for decisions
7. **Understand Context**: Consider market conditions and sector trends

---

## Advanced Usage

### Custom Scoring Weights

Modify the `_calculate_overall_score` method in `stock_selector.py` to adjust weights:

```python
def _calculate_overall_score(self, fundamental_score, technical_score, sentiment_score):
    # Custom weights: 50% Fundamental, 30% Technical, 20% Sentiment
    weights = {
        'fundamental': 0.50,
        'technical': 0.30,
        'sentiment': 0.20
    }
    
    overall_score = (
        fundamental_score * weights['fundamental'] +
        technical_score * weights['technical'] +
        sentiment_score * weights['sentiment']
    )
    
    return round(overall_score, 2)
```

### Custom Technical Period

```python
from stock_selector.technical_analysis import TechnicalAnalyzer

# Use 6 months instead of 1 year
analyzer = TechnicalAnalyzer('AAPL', period='6mo')
analysis = analyzer.analyze_technicals()
```

### Batch Processing with Progress

```python
from stock_selector import StockSelector
import time

selector = StockSelector()
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

results = []
for i, ticker in enumerate(tickers, 1):
    try:
        analysis = selector.analyze_stock(ticker)
        results.append(analysis)
        print(f"Analyzed {i}/{len(tickers)}: {ticker}")
        time.sleep(1)  # Avoid rate limiting
    except Exception as e:
        print(f"Error analyzing {ticker}: {e}")
```

---

## Support

For issues or questions:
1. Check the troubleshooting section
2. Verify ticker symbols on Yahoo Finance
3. Ensure all dependencies are installed
4. Check internet connection
5. Review error messages for specific issues
