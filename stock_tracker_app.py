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
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ["AAPL", "NVDA", "SAP", "^GDAXI", "SPY", "GC=F"]

st.sidebar.subheader("🔍 Asset hinzufügen")
search = st.sidebar.text_input("Suchen (z.B. Gold, DAX, BASF, Bitcoin)", "").upper()

if search:
    matches = {k: v for k, v in popular_assets.items() if search in k or search in v.upper()}
    if matches:
        selected_new = st.sidebar.selectbox("Gefundene Ergebnisse", options=list(matches.keys()), format_func=lambda x: f"{x} - {matches[x]}")
        if st.sidebar.button("➕ Hinzufügen"):
            if selected_new not in st.session_state.watchlist:
                st.session_state.watchlist.append(selected_new)
                st.success(f"{selected_new} hinzugefügt!")

# Watchlist verwalten
st.sidebar.subheader("Aktuelle Watchlist")
selected_tickers = st.sidebar.multiselect("Auswählen", st.session_state.watchlist, default=st.session_state.watchlist)

period = st.sidebar.selectbox("Zeitraum", ["1mo", "3mo", "6mo", "1y"], index=2)

if st.sidebar.button("🔄 Aktualisieren"):
    st.rerun()

# Daten laden & Anzeigen
data = {}
for t in selected_tickers:
    try:
        stock = yf.Ticker(t)
        hist = stock.history(period=period)
        if not hist.empty:
            data[t] = (stock, hist, stock.info, stock.news[:5] if hasattr(stock, 'news') else [])
    except:
        pass

if data:
    st.subheader("📊 Übersicht")
    rows = []
    for t, (_, hist, info, _) in data.items():
        current = hist['Close'].iloc[-1]
        change = (current - hist['Close'].iloc[-2])/hist['Close'].iloc[-2]*100 if len(hist)>1 else 0
        rows.append({
            "Symbol": t,
            "Name": info.get('longName', popular_assets.get(t, t))[:30],
            "Kurs": round(current, 2),
            "Veränderung": f"{change:+.2f}%",
            "KGV": info.get('trailingPE', 'N/A')
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    selected = st.selectbox("Detailansicht", options=list(data.keys()))
    _, hist, info, news = data[selected]

    col1, col2 = st.columns([3,1])
    with col1:
        fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'])])
        fig.update_layout(title=f"{selected} Kursverlauf", height=550)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.metric("Kurs", f"{hist['Close'].iloc[-1]:.2f}")
        st.metric("KGV", str(info.get('trailingPE', 'N/A')))
        ma50 = hist['Close'].rolling(50).mean().iloc[-1]
        emp = "🟢 KAUFEN" if hist['Close'].iloc[-1] > ma50 and (info.get('trailingPE') or 30) < 25 else "🟡 HALTEN" if hist['Close'].iloc[-1] > ma50 else "🔴 VERKAUFEN"
        st.success(f"**Empfehlung:** {emp}")

    st.subheader("📰 Nachrichten")
    for n in news:
        st.write(f"• {n.get('title')}")

else:
    st.info("Füge über die Suche Assets hinzu")

st.caption("Tipp: Suche nach 'Gold', 'DAX', 'Bitcoin', 'VWCE' etc.")
