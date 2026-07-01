import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from textblob import TextBlob

st.set_page_config(page_title="Aktien-Tracker Pro", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
</style>
""", unsafe_allow_html=True)

st.title("📈 Aktien-Tracker Pro")
st.caption("Echtzeit-Tracker mit Empfehlungen")

default_tickers = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'SAP', 'SIE', '^GDAXI', 'AMZN', 'GOOGL']
tickers_input = st.sidebar.multiselect("Watchlist", default_tickers, default=default_tickers[:6])

period = st.sidebar.selectbox("Zeitraum", ["1mo", "3mo", "6mo", "1y", "2y"], index=3)

if st.sidebar.button("🔄 Aktualisieren", type="primary"):
    st.rerun()

@st.cache_data(ttl=180)
def load_data(ticker, period):
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    info = stock.info
    news = stock.news[:6]
    return stock, hist, info, news

data = {}
for t in tickers_input:
    try:
        data[t] = load_data(t, period)
    except Exception as e:
        st.warning(f"Fehler bei {t}")

# Übersicht
if data:
    st.subheader("📊 Watchlist Übersicht")
    rows = []
    for ticker, (_, hist, info, _) in data.items():
        current = hist['Close'].iloc[-1]
        change = ((current - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2] * 100) if len(hist) > 1 else 0
        pe = info.get('trailingPE') or info.get('forwardPE')
        rows.append({
            "Ticker": ticker,
            "Kurs": round(current, 2),
            "Veränderung %": round(change, 2),
            "KGV": round(float(pe), 1) if pe else "N/A",
            "Name": info.get('longName', ticker)[:25]
        })
    
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# Detail
selected = st.selectbox("Detaillierte Ansicht", options=list(data.keys()) if data else [])

if selected and selected in data:
    _, hist, info, news = data[selected]
    
    col1, col2 = st.columns([3, 1])
    with col1:
        fig = go.Figure(data=[go.Candlestick(x=hist.index,
                        open=hist['Open'], high=hist['High'],
                        low=hist['Low'], close=hist['Close'])])
        fig.update_layout(title=f"{selected} - Kursverlauf", height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        current = hist['Close'].iloc[-1]
        st.metric("Aktueller Kurs", f"{current:.2f}")
        pe = info.get('trailingPE') or info.get('forwardPE')
        st.metric("KGV (P/E)", f"{pe:.1f}" if pe else "N/A")
        
        ma50 = hist['Close'].rolling(50).mean().iloc[-1]
        empfehlung = "🟢 **KAUFEN**" if current > ma50 and (pe or 30) < 25 else "🟡 **HALTEN**" if current > ma50 else "🔴 **VERKAUFEN**"
        st.success(f"**Empfehlung:**\n{empfehlung}")

    st.subheader("📰 Nachrichten")
    for n in news:
        sent = TextBlob(n.get('title', '')).sentiment.polarity
        emoji = "🟢" if sent > 0.05 else "🔴" if sent < -0.05 else "⚪"
        st.write(f"{emoji} {n.get('title')}")

st.caption("Datenquelle: Yahoo Finance • Keine Anlageberatung")
