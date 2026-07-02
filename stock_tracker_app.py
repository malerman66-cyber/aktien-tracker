import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Aktien Tracker", layout="wide")

st.title("📈 Aktien & ETF Tracker")

# Einfache Watchlist
tickers = st.multiselect(
    "Wähle Assets",
    ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'SAP', 'SIE', 'AIR', '^GDAXI', 'SPY', 'QQQ', 'GC=F', 'SI=F', 'BTC-USD'],
    default=['AAPL', 'NVDA', 'SAP', '^GDAXI', 'SPY', 'GC=F']
)

period = st.selectbox("Zeitraum", ["1mo", "3mo", "6mo", "1y"], index=2)

if st.button("🔄 Aktualisieren"):
    st.rerun()

data = {}
for t in tickers:
    try:
        stock = yf.Ticker(t)
        hist = stock.history(period=period)
        if not hist.empty:
            data[t] = hist
    except:
        st.warning(f"Fehler bei {t}")

if data:
    st.subheader("Kursübersicht")
    summary = []
    for t, hist in data.items():
        current = hist['Close'].iloc[-1]
        change = (current - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2] * 100 if len(hist) > 1 else 0
        summary.append({"Ticker": t, "Kurs": round(current,2), "Veränderung %": round(change,2)})
    st.dataframe(pd.DataFrame(summary), use_container_width=True)

    selected = st.selectbox("Detailansicht", list(data.keys()))
    hist = data[selected]
    
    fig = go.Figure(data=[go.Candlestick(x=hist.index,
                    open=hist['Open'], high=hist['High'],
                    low=hist['Low'], close=hist['Close'])])
    fig.update_layout(title=f"{selected} Kursverlauf", height=600)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Wähle Assets aus")

st.caption("Daten von Yahoo Finance")
