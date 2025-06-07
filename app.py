import streamlit as st
import yfinance as yf
import plotly.graph_objs as go

st.set_page_config(page_title="ICT SMT Divergence Dashboard", layout="wide")
st.title("📊 ICT SMT Divergence Detector (EUR/USD vs DXY)")

@st.cache_data(ttl=900)
def fetch_data(ticker, period="2d", interval="60m"):
    df = yf.download(tickers=ticker, period=period, interval=interval)
    df = df[['Close']].rename(columns={'Close': ticker})
    return df

# Fetch EUR/USD and DXY data
eurusd = fetch_data("EURUSD=X")
dxy = fetch_data("DX-Y.NYB")

col1, col2 = st.columns(2)

with col1:
    st.subheader("EUR/USD (60min)")
    if eurusd.empty:
        st.warning("⚠️ Could not fetch EUR/USD data.")
    else:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=eurusd.index, y=eurusd["EURUSD=X"], mode='lines+markers', name="EUR/USD"))
        st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("DXY (60min)")
    if dxy.empty:
        st.warning("⚠️ Could not fetch DXY data.")
    else:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=dxy.index, y=dxy["DX-Y.NYB"], mode='lines+markers', name="DXY"))
        st.plotly_chart(fig2, use_container_width=True)
