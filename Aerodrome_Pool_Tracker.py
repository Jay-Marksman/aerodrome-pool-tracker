import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import re
import time

DEX_SCREENER_PAIR_URL = "https://api.dexscreener.com/latest/dex/pairs"


@st.cache_data(ttl=60)
def fetch_pair(chain: str, pool_address: str, max_retries: int = 2):
    """
    Fetch pair data from Dex Screener with retry logic.
    Returns a single pair dict or None.
    """
    url = f"{DEX_SCREENER_PAIR_URL}/{chain}/{pool_address}"
    
    for attempt in range(max_retries + 1):
        try:
            response = requests.get(url, timeout=10)
        except requests.RequestException as e:
            if attempt == max_retries:
                st.error(f"Network error for {pool_address} after {max_retries+1} tries: {e}")
                return None
            time.sleep(1)
            continue

        if response.status_code != 200:
            if attempt == max_retries:
                st.error(f"Error fetching data for {pool_address}: {response.text}")
                return None
            time.sleep(1)
            continue

        data = response.json()
        pairs = data.get("pairs", [])
        if not pairs:
            st.warning(f"No pair data returned from Dex Screener for {pool_address}.")
            return None

        return pairs[0]
    
    return None


def is_valid_address(addr: str) -> bool:
    """Validate 0x-prefixed hex address."""
    pattern = r'^0x[a-fA-F0-9]{40}$'
    return bool(re.match(pattern, addr))


def build_dataframe_from_pair(pair: dict) -> pd.DataFrame:
    """
    Flatten a single Dex Screener pair object into a one-row DataFrame.
    """
    base_token = pair.get("baseToken", {}) or {}
    quote_token = pair.get("quoteToken", {}) or {}
    liquidity = pair.get("liquidity", {}) or {}
    volume = pair.get("volume", {}) or {}
    
    # Txns object: handle both "count" and "buys + sells" formats
    txns = pair.get("txns", {}) or {}
    tx_24h = txns.get("h24") or {}
    tx_6h = txns.get("h6") or {}
    tx_1h = txns.get("h1") or {}

    # Robust tx count extraction
    def get_tx_count(tx_window):
        return int(tx_window.get("count") or 
                  (tx_window.get("buys", 0) + tx_window.get("sells", 0)))

    row = {
        "pair_address": pair.get("pairAddress"),
        "dex": pair.get("dexId"),
        "chain": pair.get("chainId"),

        "token0_symbol": base_token.get("symbol"),
        "token0_address": base_token.get("address"),
        "token1_symbol": quote_token.get("symbol"),
        "token1_address": quote_token.get("address"),

        "price_usd": float(pair.get("priceUsd") or 0),

        "liquidity_usd": float(liquidity.get("usd") or 0),
        "liquidity_token0": float(liquidity.get("base") or 0),
        "liquidity_token1": float(liquidity.get("quote") or 0),

        "volume_24h_usd": float(volume.get("h24") or 0),
        "volume_6h_usd": float(volume.get("h6") or 0),
        "volume_1h_usd": float(volume.get("h1") or 0),

        "tx_24h_count": get_tx_count(tx_24h),
        "tx_6h_count": get_tx_count(tx_6h),
        "tx_1h_count": get_tx_count(tx_1h),

        "tx_24h_buys": int(tx_24h.get("buys") or 0),
        "tx_24h_sells": int(tx_24h.get("sells") or 0),
    }

    return pd.DataFrame([row])


def main():
    st.title("Aerodrome Pool Tracker")

    st.sidebar.header("Settings")
    addresses_input = st.sidebar.text_area(
        "Aerodrome pool addresses on Base (one per line)",
        value="0x...\n0x...",
        height=120,
    )

    refresh_btn = st.sidebar.button("🔄 Refresh Data (30s cache)")

    # Parse and validate addresses
    raw_addresses = [a.strip() for a in addresses_input.splitlines()]
    pool_addresses = []
    for addr in raw_addresses:
        if not addr or addr == "0x...":
            continue
        if is_valid_address(addr):
            pool_addresses.append(addr)
        else:
            st.sidebar.warning(f"❌ Invalid address: {addr}")

    if not pool_addresses:
        st.info("Enter at least one valid Aerodrome pool address (one per line).")
        return

    st.sidebar.success(f"✅ Validated {len(pool_addresses)} pools")

    # Fetch all pools
    all_rows = []
    first_pair = None
    valid_pools = 0

    for addr in pool_addresses:
        pair = fetch_pair("base", addr.lower())
        if pair is None:
            continue
        
        if first_pair is None:
            first_pair = pair
        
        df_row = build_dataframe_from_pair(pair)
        all_rows.append(df_row)
        valid_pools += 1

    if not all_rows:
        st.error("No valid pairs fetched from Dex Screener.")
        return

    df = pd.concat(all_rows, ignore_index=True)
    st.success(f"✅ Loaded {valid_pools} pools")

    # Debug expander (safe)
    if first_pair is not None:
        with st.expander("🔍 Debug: Raw JSON for first pool"):
            import json
            st.code(json.dumps(first_pair, indent=2))

    # Pools overview table
    st.subheader("Pools Overview")
    display_cols = [
        "pair_address",
        "token0_symbol",
        "token1_symbol",
        "price_usd",
        "liquidity_usd",
        "volume_24h_usd",
        "tx_24h_count",
    ]
    st.dataframe(df[display_cols], use_container_width=True)

    # Aggregate metrics
    st.subheader("Aggregate Metrics (All Pools)")
    total_liquidity = df["liquidity_usd"].sum()
    total_volume_24h = df["volume_24h_usd"].sum()
    total_trades_24h = df["tx_24h_count"].sum()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Liquidity (USD)", f"{total_liquidity:,.0f}")
    with col2:
        st.metric("Total Volume 24h (USD)", f"{total_volume_24h:,.0f}")
    with col3:
        st.metric("Total Trades 24h", f"{total_trades_24h:,}")

    # Charts
    st.subheader("Volume 24h by Pool")
    fig_vol = px.bar(
        df,
        x="pair_address",
        y="volume_24h_usd",
        hover_data=["token0_symbol", "token1_symbol"],
        title="24h Volume by Pool",
    )
    st.plotly_chart(fig_vol, use_container_width=True)

    st.subheader("Liquidity (USD) by Pool")
    fig_liq = px.bar(
        df,
        x="pair_address",
        y="liquidity_usd",
        hover_data=["token0_symbol", "token1_symbol"],
        title="Liquidity by Pool",
    )
    st.plotly_chart(fig_liq, use_container_width=True)

    # Liquidity vs Volume scatter
    st.subheader("Liquidity vs 24h Volume")
    fig_scatter = px.scatter(
        df,
        x="liquidity_usd",
        y="volume_24h_usd",
        size="tx_24h_count",
        hover_data=["token0_symbol", "token1_symbol", "pair_address"],
        title="Pool Size vs Activity (size = trades)",
        labels={"liquidity_usd": "Liquidity (USD)", "volume_24h_usd": "Volume 24h (USD)"}
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # Per-pool details
    st.subheader("Per-Pool Details")
    for _, row in df.iterrows():
        with st.expander(f"{row['token0_symbol']}/{row['token1_symbol']} – {row['pair_address'][:12]}..."):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("Price (USD)", f"{row['price_usd']:,.4f}")
            with c2:
                st.metric("Liquidity (USD)", f"{row['liquidity_usd']:,.0f}")
            with c3:
                st.metric("Volume 24h (USD)", f"{row['volume_24h_usd']:,.0f}")
            with c4:
                st.metric("Trades 24h", f"{row['tx_24h_count']:,}")


if __name__ == "__main__":
    main()

