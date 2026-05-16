# Stock Selector

A comprehensive stock selection tool that combines fundamental analysis, technical analysis, and news sentiment to identify promising investment opportunities.

## Features

### Fundamental Analysis
- Market Cap analysis
- Last Traded Price (LTP)
- Price-to-Earnings (P/E) ratio
- Earnings Per Share (EPS)
- PEG ratio
- Return on Capital Employed (ROCE)
- Return on Equity (ROE)
- Quarterly Results analysis
- Profit & Loss statements
- Balance Sheet analysis
- Shareholding Pattern analysis

### Technical Analysis
- 200-day Simple Moving Average (SMA)
- Relative Strength Index (RSI)
- 52-week high/low analysis
- Price vs SMA comparison
- Distance from 52-week high/low

### News & Sentiment
- Latest news aggregation
- Sentiment analysis (VADER and TextBlob)
- Earnings results analysis
- News volume tracking

### Scoring System
- Fundamental Score (0-100): Based on P/E, PEG, ROE, ROCE, Market Cap
- Technical Score (0-100): Based on SMA, RSI, 52-week position
- Sentiment Score (0-100): Based on news sentiment and earnings news
- Overall Score (0-100): Weighted combination (40% Fundamental, 35% Technical, 25% Sentiment)
- Investment Recommendation: Strong Buy, Buy, Moderate Buy, Hold, Moderate Sell, Sell, Strong Sell

## Installation

```bash
cd /Users/admin/Documents/Learn_Backend/stock_selector
pip install -r requirements.txt
```

## Usage

### Python API

```python
from stock_selector import StockSelector

# Initialize selector
selector = StockSelector()

# Analyze a single stock
analysis = selector.analyze_stock('AAPL')
print(f"Overall Score: {analysis['overall_score']}/100")
print(f"Recommendation: {analysis['recommendation']}")

# Get detailed report
report = selector.get_detailed_report('AAPL')
print(report)

# Analyze multiple stocks
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
ranked_stocks = selector.analyze_multiple_stocks(tickers)
print(ranked_stocks)

# Get top N stocks
top_stocks = selector.get_top_stocks(tickers, top_n=5)
print(top_stocks)

# Filter stocks by criteria
filtered = selector.filter_stocks(
    tickers,
    min_fundamental_score=50,
    min_technical_score=50,
    min_sentiment_score=40
)
print(filtered)
```

### Command Line Interface

```bash
# Analyze a single stock
python -m stock_selector analyze AAPL

# Generate detailed report
python -m stock_selector analyze AAPL --report

# Analyze multiple stocks
python -m stock_selector multi AAPL MSFT GOOGL AMZN TSLA

# Get top 5 stocks
python -m stock_selector multi AAPL MSFT GOOGL AMZN TSLA --top 5

# Export to CSV
python -m stock_selector multi AAPL MSFT GOOGL --output csv

# Filter stocks by criteria
python -m stock_selector filter AAPL MSFT GOOGL --min-fundamental 50 --min-technical 50 --min-sentiment 40
```

### Individual Analyzers

```python
from stock_selector.fundamental_analysis import FundamentalAnalyzer
from stock_selector.technical_analysis import TechnicalAnalyzer
from stock_selector.news_sentiment import NewsSentimentAnalyzer

# Fundamental analysis only
fund_analyzer = FundamentalAnalyzer('AAPL')
fund_analysis = fund_analyzer.analyze_fundamentals()
print(fund_analyzer.get_fundamental_summary())

# Technical analysis only
tech_analyzer = TechnicalAnalyzer('AAPL')
tech_analysis = tech_analyzer.analyze_technicals()
print(tech_analyzer.get_technical_summary())

# Sentiment analysis only
sentiment_analyzer = NewsSentimentAnalyzer('AAPL')
sentiment_analysis = sentiment_analyzer.analyze_sentiment()
print(sentiment_analyzer.get_sentiment_summary())
```

## Project Structure

```
stock_selector/
├── stock_selector/
│   ├── __init__.py
│   ├── stock_selector.py          # Main StockSelector class
│   ├── cli.py                     # Command-line interface
│   ├── fundamental_analysis/
│   │   ├── __init__.py
│   │   └── analyzer.py            # Fundamental analysis implementation
│   ├── technical_analysis/
│   │   ├── __init__.py
│   │   └── analyzer.py            # Technical analysis implementation
│   ├── news_sentiment/
│   │   ├── __init__.py
│   │   └── analyzer.py            # News sentiment analysis implementation
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py             # Utility functions
│   └── data/
├── examples/
│   └── basic_usage.py             # Example usage
├── tests/
├── docs/
├── requirements.txt
├── setup.py
└── README.md
```

## Dependencies

- yfinance: Stock data fetching
- pandas: Data manipulation
- numpy: Numerical operations
- ta: Technical analysis indicators
- vaderSentiment: Sentiment analysis
- textblob: Text sentiment analysis
- beautifulsoup4: HTML parsing

## Scoring Criteria

### Fundamental Score (0-100)
- P/E Ratio (20 points): <15 (20), <25 (15), <40 (10), <60 (5)
- PEG Ratio (20 points): <1.0 (20), <1.5 (15), <2.0 (10), <3.0 (5)
- ROE (20 points): >20% (20), >15% (15), >10% (10), >5% (5)
- ROCE (20 points): >20% (20), >15% (15), >10% (10), >5% (5)
- Market Cap (20 points): Mid-cap preferred

### Technical Score (0-100)
- Price vs 200 SMA (30 points): Above (30), Below (10)
- RSI (40 points): 30-70 (40), <30 (35), <40 (30), >70 (10), >60 (20)
- 52-week Position (30 points): Balanced position preferred

### Sentiment Score (0-100)
- Overall Sentiment (50 points): Positive (50), Neutral (30), Negative (10)
- Earnings Sentiment (30 points): Positive (30), Neutral (15), Negative (5)
- News Volume (20 points): More news indicates more interest

### Overall Score
- Fundamental: 40% weight
- Technical: 35% weight
- Sentiment: 25% weight

## License

MIT License

# Directory Structure

├── .windsurf
│   └── workflows
│       ├── model.md
├── docs
│   ├── USAGE_GUIDE.md
├── examples
│   ├── basic_usage.py
├── stock_selector
│   ├── fundamental_analysis
│   │   ├── __init__.py
│   │   ├── analyzer.py
│   ├── news_sentiment
│   │   ├── __init__.py
│   │   ├── analyzer.py
│   ├── technical_analysis
│   │   ├── __init__.py
│   │   ├── analyzer.py
│   └── utils
│       ├── __init__.py
│       ├── helpers.py
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── stock_selector.py
└── webapp
    ├── static
    │   ├── css
    │   │   ├── style.css
    │   └── js
    │       ├── app.js
    │       ├── autocomplete.js
    │       ├── chart.js
    └── templates
        ├── index.html
    ├── .gitignore
    ├── DEPLOYMENT.md
    ├── NGINX_SETUP.md
    ├── Procfile
    ├── README.md
    ├── app.py
    ├── gunicorn.service
    ├── nginx.conf
    ├── patch_html.py
    ├── render.yaml
    ├── requirements.txt
    ├── runtime.txt
├── .gitignore
├── README.md
├── requirements.txt
├── setup.py

# End Directory Structure