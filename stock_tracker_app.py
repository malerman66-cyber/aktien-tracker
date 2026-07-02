import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Aktien-Tracker Pro", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
</style>
""", unsafe_allow_html=True)

st.title("📈 Aktien-Tracker Pro")
st.caption("Mit ETFs & Indizes • Suchfunktion")

# Session State
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = [
        'AAPL', 'MSFT', 'NVDA', 'TSLA', 'SAP', 'SIE', '^GDAXI', 
        'SPY', 'QQQ', 'VOO', '^GSPC', '^IXIC', 'DAX'
    ]

# Suchfunktion
st.sidebar.subheader("🔍 Ticker hinzufügen")
new_ticker = st.sidebar.text_input("Ticker (z.B. BAS, VWCE, ^STOXX)", "").upper().strip()

if st.sidebar.button("➕ Hinzufügen") and new_ticker:
    if new_ticker not in st.session_state.watchlist:
        st.session_state.watchlist.append(new_ticker)
        st.success(f"{new_ticker} hinzugefügt!")
    else:
        st.warning("Schon in der Liste")

# Watchlist
st.sidebar.subheader("Deine Watchlist")
selected_tickers = st.sidebar.multiselect("Auswählen", 
                                        options=st.session_state.watchlist, 
                                        default=st.session_state.watchlist)

period = st.sidebar.selectbox("Zeitraum", ["1mo", "3mo", "6mo", "1y"], index=2)

if st.sidebar.button("🔄 Aktualisieren"):
    st.rerun()

# Daten laden
data = {}
for t in selected_tickers:
    try:
        stock = yf.Ticker(t)
        hist = stock.history(period=period)
        if not hist.empty:
            info = stock.info
            news = stock.news[:5] if hasattr(stock, 'news') else []
            data[t] = (stock, hist, info, news)
    except:
        pass

# Übersicht
st.subheader("📊 Watchlist")
if data:
    rows = []
    for ticker, (_, hist, info, _) in data.items():
        current = hist['Close'].iloc[-1]
        change = (current - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2] * 100 if len(hist) > 1 else 0
        pe = info.get('trailingPE') or info.get('forwardPE')
        rows.append({
            "Ticker": ticker,
            "Kurs": round(current, 2),
            "± %": round(change, 2),
            "KGV": round(pe, 1) if pe else "-",
            "Name": info.get('longName', ticker)[:28]
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# Detailansicht
if data:
    selected = st.selectbox("Detaillierte Ansicht", list(data.keys()))
    _, hist, info, news = data[selected]
    
    col1, col2 = st.columns([3,1])
    with col1:
        fig = go.Figure(data=[go.Candlestick(x=hist.index,
                        open=hist['Open'], high=hist['High'],
                        low=hist['Low'], close=hist['Close'])])
        fig.update_layout(title=f"{selected} - Kursverlauf", height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.metric("Kurs", f"{hist['Close'].iloc[-1]:.2f}")
        pe = info.get('trailingPE') or info.get('forwardPE')
        st.metric("KGV", f"{pe:.1f}" if pe else "N/A")
        
        ma50 = hist['Close'].rolling(50).mean().iloc[-1]
        emp = "🟢 KAUFEN" if hist['Close'].iloc[-1] > ma50 and (pe or 30) < 25 else "🟡 HALTEN" if hist['Close'].iloc[-1] > ma50 else "🔴 VERKAUFEN"
        st.success(f"**Empfehlung:** {emp}")

    st.subheader("📰 Nachrichten")
    for n in news:
        st.write(f"• {n.get('title', 'Keine aktuellen Nachrichten')}")

st.caption("Beispiele: VWCE.DE, EUNL.DE, ^STOXX, QQQ, SPY, IWM")
