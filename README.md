# Aerodrome Pool Tracker (Dex Screener)

Real-time dashboard for tracking multiple Aerodrome pools on Base using [Dex Screener API](https://docs.dexscreener.com/api/reference).

## ✨ Features

- Track **multiple pools** (paste addresses, one per line)
- Live metrics: price, liquidity, 24h volume, trades
- Charts: volume by pool, liquidity vs volume scatter plot
- Address validation and retry logic
- 60s auto‑caching for performance

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ 
- Git

### 1. Install dependencies
```bash
pip3 install -r requirements.txt
# OR install individually:
# pip3 install streamlit requests pandas plotly

