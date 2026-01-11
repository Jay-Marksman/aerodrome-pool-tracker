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
```
bash
pip3 install -r requirements.txt
# OR install individually:
# pip3 install streamlit requests pandas plotly
```

### 2. Add streamlit to PATH (Linux/macOS)

```
bash
export PATH=$PATH:~/.local/bin
```

### 3. Run the app

```
bash
streamlit run Aerodrome_Pool_Tracker.py
```

### 4. Open your browser

Streamlit will open http://localhost:8501 automatically.
📱 Usage

-    Paste Aerodrome pool addresses (one per line) in the sidebar

-    Click "Refresh Data" or wait for 60s cache refresh

-    View:

        Overview table of all pools

        Aggregate metrics across selected pools

        Charts (volume, liquidity, scatter)

        Per-pool details (expandable)

Example pool addresses

```
0x9Da64ed1b87b3d0d3d1E731dd3aAAAc08eb0f5C3
0x80c394f8867e06704d39a5910666a3e71ca7f325
0xdb6556a14976894a01085c2abf3c85c86d1c15c8
```

🔧 Customization
Add your own pools

Paste any Aerodrome/Base pool addresses in the sidebar text area.
Modify refresh rate

Edit ttl=60 in @st.cache_data(ttl=60) (seconds).
Debug mode

Expand "🔍 Debug: Raw JSON" to see Dex Screener's raw response.
🛠 Troubleshooting

"streamlit: command not found"

bash
export PATH=$PATH:~/.local/bin
# Add to ~/.bashrc or ~/.zshrc for permanent fix

No data for pool

-    Verify it's an Aerodrome pool on Base

-    Check address format (42 chars, starts with 0x)

-    Use debug expander to see Dex Screener response

Charts empty

-    Ensure at least 2 valid pools loaded

-    Check debug JSON for data structure

📊 Data Source

Powered by Dex Screener API:

-    priceUsd, liquidity.usd, volume.h24, txns.h24.count

-    No API key needed (public rate limits apply)

###Made with ❤️ for Base DeFi degens###

