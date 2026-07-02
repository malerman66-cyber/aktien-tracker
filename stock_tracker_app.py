import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Aktien-Tracker Pro", layout="wide")

st.title("📈 Aktien & ETF Tracker Pro")

# Vordefinierte Assets mit Symbolen
popular_assets = {
    "AAPL": "🍎 Apple", "MSFT": "💻 Microsoft", "NVDA": "🤖 NVIDIA",
    "TSLA": "🚗 Tesla", "SAP": "🇩🇪 SAP", "SIE": "⚡ Siemens",
    "AIR": "✈️ Airbus", "ALV": "🛡️ Allianz", "BAS": "🧪 BASF",
    "BMW": "🏎️ BMW", "VOW3": "🏭 Volkswagen",
    "^GDAXI": "🇩🇪 DAX", "^GSPC": "🇺🇸 S&P 500", "^IXIC": "🇺🇸 Nasdaq",
    "SPY": "📊 S&P 500 ETF", "QQQ": "🚀 Nasdaq 100 ETF",
    "VOO": "📈 Vanguard S&P 500", "VWCE.DE": "🌍 Vanguard All-World",
    "EUNL.DE": "🌍 iShares MSCI World", "GC=F": "🥇 Gold",
    "SI=F": "🥈 Silber", "BTC-USD": "₿ Bitcoin"
}

if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ["AAPL", "NVDA", "SAP", "^GDAXI", "SPY", "GC=F"]

st.sidebar.subheader("🔍 Asset suchen & hinzufügen")
search = st.sidebar.text_input("Suchen (z.B. Gold, DAX, BASF, Bitcoin)", "").strip()

if search:
    matches = {k:v for k,v in popular_assets.items() if search.upper() in k.upper() or search.upper() in v.upper()}
    if matches:
        choice = st.sidebar.selectbox("Ergebnisse", options=list(matches.keys()), format_func=lambda x: f"{x} — {matches[x]}")
        if st.sidebar.button("➕ Hinzufügen"):
            if choice not in st.session_state.watchlist:
                st.session_state.watchlist.append(choice)
                st.success(f"{choice} hinzugefügt")

st.sidebar.subheader("Watchlist")
selected_tickers = st.sidebar.multiselect("Auswählen", st.session_state.watchlist, default=st.session_state.watchlist)

period = st.sidebar.selectbox("Zeitraum", ["1mo", "3mo", "6mo", "1y"], index=2)

if st.sidebar.button("🔄 Aktualisieren"):
    st.rerun()

# Daten
data = {}
for t in selected_tickers:
    try:
        stock = yf.Ticker(t)
        hist = stock.history(period=period)
        if not hist.empty:
            data[t] = (stock, hist, stock.info, getattr(stock, 'news', [])[:5])
    except:
        st.sidebar.warning(f"Keine Daten für {t}")

# Übersicht
if data:
    st.subheader("📊 Übersicht")
    rows = []
    for t, (_, hist, info, _) in data.items():
        current = hist['Close'].iloc[-1]
        change = (current - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2] * 100 if len(hist) > 1 else 0
        rows.append({
            "Symbol": t,
            "Name": info.get('longName', popular_assets.get(t, t))[:35],
            "Kurs": round(current, 2),
            "Veränderung": f"{change:+.2f}%",
            "KGV": info.get('trailingPE', 'N/A')
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # Detail
    selected = st.selectbox("Detailansicht", list(data.keys()))
    _, hist, info, news = data[selected]
    
    col1, col2 = st.columns([3,1])
    with col1:
        fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high
