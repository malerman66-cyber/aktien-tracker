import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Aktien-Tracker Pro", layout="wide")

st.title("📈 Aktien & ETF Tracker Pro")
st.caption("Suche + Große Auswahl")

# Große vordefinierte Liste
popular_assets = {
    "AAPL": "🍎 Apple",
    "MSFT": "💻 Microsoft",
    "NVDA": "🤖 NVIDIA",
    "TSLA": "🚗 Tesla",
    "SAP": "🇩🇪 SAP",
    "SIE": "⚡ Siemens",
    "AIR": "✈️ Airbus",
    "ALV": "🛡️ Allianz",
    "BAS": "🧪 BASF",
    "BMW": "🏎️ BMW",
    "VOW3": "🏭 Volkswagen",
    "^GDAXI": "🇩🇪 DAX",
    "^GSPC": "🇺🇸 S&P 500",
    "^IXIC": "🇺🇸 Nasdaq",
    "SPY": "📊 S&P 500 ETF",
    "QQQ": "🚀 Nasdaq 100 ETF",
    "VOO": "📈 Vanguard S&P 500",
    "VWCE.DE": "🌍 Vanguard FTSE All-World",
    "EUNL.DE": "🌍 iShares Core MSCI World",
    "GC=F": "🥇 Gold",
    "SI=F": "🥈 Silber",
    "BTC-USD": "₿ Bitcoin",
    "ETH-USD": "⧫ Ethereum"
}

# Session Watchlist
if 'watchlist' not
