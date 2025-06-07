import streamlit as st
import requests
import pandas as pd
import plotly.graph_objs as go

st.set_page_config(page_title="ICT SMT Divergence Dashboard", layout="wide")
st.title("📊 ICT SMT Divergence Detector (EUR/USD vs DXY)")

# Input API key
api_key = st.secrets["ALPHA_VANTAGE_KEY"] if "ALPHA_VANTAGE_KEY" in st.secrets else st.text_input("Enter Alpha Vantage API Key")

@st.cache_data(ttl=300)
def fetch_fx_intraday(symbol_from, symbol_to):
    url = f"https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol={symbol_from}&to_symbol={symbol_to}&interval=15min&outputsize=compact&apikey={api_key}"
    response = requests.get(url).json()
    data = response.get("Time Series FX (15min)", {})
    df = pd.DataFrame.from_dict(data, orient='index')
    df.columns = ["open", "high", "low", "close"]
    df = df.astype(float).sort_index()
    return df

@st.cache_data(ttl=300)
def fetch_dxy_intraday():
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=UUP&interval=15min&outputsize=compact&apikey={api_key}"
    response = requests.get(url).json()
    data = response.get("Time Series (15min)", {})
    df = pd.DataFrame.from_dict(data, orient='index')
    df.columns = ["open", "high", "low", "close", "volume"]
    df = df.astype(float).sort_index()
    return df

if api_key:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("EUR/USD (15min)")
        eurusd = fetch_fx_intraday("EUR", "USD")
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=eurusd.index, y=eurusd["close"], mode='lines+markers', name="EUR/USD"))
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("DXY Proxy via UUP ETF (15min)")
        dxy = fetch_dxy_intraday()
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=dxy.index, y=dxy["close"], mode='lines+markers', name="DXY"))
        st.plotly_chart(fig2, use_container_width=True)
