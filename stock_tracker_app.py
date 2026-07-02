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
st.caption("Echtzeit Börsen App")

default_tickers = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'SAP', 'SIE', 'AIR', '^GDAXI', 'AMZN', 'GOOGL']
tickers_input = st.sidebar.multiselect("Watchlist", default_tickers, default=default_tickers[:7])

period = st.sidebar.selectbox("Zeitraum", ["1mo", "3mo", "6mo", "1y"], index=2)

if st.sidebar.button("🔄 Jetzt aktualisieren"):
    st.rerun()

data = {}
for t in tickers_input:
    try:
        stock = yf.Ticker(t)
        hist = stock.history(period=period)
        info = stock.info
        news = stock.news[:5]
        data[t] = (stock, hist, info, news)
    except:
        st.warning(f"Probleme mit {t}")

# Übersicht
st.subheader("📊 Watchlist")
if data:
    rows = []
    for ticker, (_, hist, info, _) in data.items():
        if len(hist) > 1:
            current = hist['Close'].iloc[-1]
            change = (current - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2] * 100
            pe = info.get('trailingPE') or info.get('forwardPE')
            rows.append({
                "Ticker": ticker,
                "Kurs": round(current, 2),
                "Veränderung %": round(change, 2),
                "KGV": round(pe, 1) if pe else "N/A",
                "Name": info.get('longName', ticker)[:25]
            })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# Detail
if data:
    selected = st.selectbox("Detailansicht", options=list(data.keys()))
    _, hist, info, news = data[selected]
    
    col1, col2 = st.columns([3,1])
    with col1:
        fig = go.Figure(data=[go.Candlestick(x=hist.index,
                        open=hist['Open'], high=hist['High'],
                        low=hist['Low'], close=hist['Close'])])
        fig.update_layout(title=f"{selected} - Kursverlauf", height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        current = hist['Close'].iloc[-1]
        st.metric("Kurs", f"{current:.2f}")
        pe = info.get('trailingPE') or info.get('forwardPE')
        st.metric("KGV", str(round(pe,1) if pe else "N/A"))
        
        ma = hist['Close'].rolling(50).mean().iloc[-1]
        emp = "🟢 KAUFEN" if current > ma and (pe or 30) < 25 else "🟡 HALTEN" if current > ma else "🔴 VERKAUFEN"
        st.success(f"**Empfehlung:** {emp}")

    st.subheader("📰 Nachrichten")
    for n in news:
        st.write(f"• {n.get('title')}")

st.caption("Daten von Yahoo Finance • Keine Anlageberatung")
