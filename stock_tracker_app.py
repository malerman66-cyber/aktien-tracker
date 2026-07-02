 import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Aktien-Tracker Pro", layout="wide", initial_sidebar_state="expanded")

# Schönes Dark Design
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    .metric { font-size: 1.2rem; }
</style>
""", unsafe_allow_html=True)

st.title("📈 Aktien-Tracker Pro")
st.caption("Echtzeit | Mobile optimiert | Automatisch aktualisiert")

# Erweiterte Watchlist
default_tickers = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'SAP', 'SIE', 'AIR', '^GDAXI', 'AMZN', 'GOOGL', 'META', 'VOW3']
tickers_input = st.sidebar.multiselect("Deine Watchlist", options=default_tickers, default=default_tickers[:8])

period = st.sidebar.selectbox("Zeitraum", ["1mo", "3mo", "6mo", "1y"], index=2)
auto_refresh = st.sidebar.checkbox("Automatisch alle 5 Min aktualisieren", value=True)

@st.cache_data(ttl=300)
def load_data(ticker, period):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        info = stock.info
        news = stock.news[:5]
        return stock, hist, info, news
    except:
        return None, None, {}, []

data = {}
for t in tickers_input:
    result = load_data(t, period)
    if result[1] is not None:
        data[t] = result

if auto_refresh:
    st.caption(f"🔄 Nächste Aktualisierung in 5 Minuten • {datetime.now().strftime('%H:%M')}")

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
            "Kurs": f"{current:.2f}",
            "± %": f"{change:+.2f}",
            "KGV": f"{round(pe,1) if pe else 'N/A'}",
            "Name": info.get('longName', ticker)[:22]
        })
    
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# Detailansicht
selected = st.selectbox("Detaillierte Ansicht", options=list(data.keys()))

if selected:
    _, hist, info, news = data[selected]
    
    col1, col2 = st.columns([3,1])
    with col1:
        fig = go.Figure(data=[go.Candlestick(x=hist.index,
                        open=hist['Open'], high=hist['High'],
                        low=hist['Low'], close=hist['Close'])])
        fig.update_layout(title=f"{selected} Kursverlauf", height=480)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        current = hist['Close'].iloc[-1]
        st.metric("Aktueller Kurs", f"{current:.2f}")
        pe = info.get('trailingPE') or info.get('forwardPE')
        st.metric("KGV", f"{pe:.1f}" if pe else "N/A")
        
        ma50 = hist['Close'].rolling(50).mean().iloc[-1]
        emp = "🟢 KAUFEN" if current > ma50 and (pe or 30) < 25 else "🟡 HALTEN" if current > ma50 else "🔴 VERKAUFEN"
        st.success(f"**Empfehlung:**\n{emp}")

    st.subheader("📰 Nachrichten")
    for n in news:
        st.write(f"• {n.get('title', 'Keine Titel')}")

st.caption("Daten von Yahoo Finance • Keine Finanzberatung")
