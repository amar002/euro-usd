import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objs as go

st.set_page_config(page_title="ICT SMT Divergence Dashboard", layout="wide")
st.title("📊 ICT SMT Divergence Detector (EUR/USD vs DXY)")

@st.cache_data(ttl=900)
def fetch_data(ticker, period="2d", interval="60m"):
    df = yf.download(tickers=ticker, period=period, interval=interval)
    df = df[['Close']].rename(columns={'Close': ticker})
    return df

# Fetch data
eurusd = fetch_data("EURUSD=X")
dxy = fetch_data("DX-Y.NYB")

# 🧼 Clean & align time indexes
eurusd.index = pd.to_datetime(eurusd.index)
dxy.index = pd.to_datetime(dxy.index)

eurusd = eurusd.resample("60min").last().dropna()
dxy = dxy.resample("60min").last().dropna()

common_index = eurusd.index.intersection(dxy.index)
eurusd = eurusd.loc[common_index]
dxy = dxy.loc[common_index]

# 📉 Detect local highs/lows
def find_local_extrema(series, window=3):
    lows = (series.shift(1) > series) & (series.shift(-1) > series)
    highs = (series.shift(1) < series) & (series.shift(-1) < series)
    return series[lows], series[highs]

# 🔍 Detect SMT divergence
def detect_smt_divergence(eur_df, dxy_df):
    signal_log = []

    eur_lows, eur_highs = find_local_extrema(eur_df["EURUSD=X"])
    dxy_lows, dxy_highs = find_local_extrema(dxy_df["DX-Y.NYB"])

    if len(eur_lows) < 2 or len(eur_highs) < 2 or len(dxy_lows) < 2 or len(dxy_highs) < 2:
        return signal_log

    eur_low_recent = eur_lows.iloc[-1]
    eur_low_prev = eur_lows.iloc[-2]
    dxy_high_recent = dxy_highs.iloc[-1]
    dxy_high_prev = dxy_highs.iloc[-2]

    eur_high_recent = eur_highs.iloc[-1]
    eur_high_prev = eur_highs.iloc[-2]
    dxy_low_recent = dxy_lows.iloc[-1]
    dxy_low_prev = dxy_lows.iloc[-2]

    if eur_low_recent < eur_low_prev and dxy_high_recent < dxy_high_prev:
        signal_log.append(("Bullish SMT Divergence", eur_lows.index[-1]))

    if eur_high_recent > eur_high_prev and dxy_low_recent > dxy_low_prev:
        signal_log.append(("Bearish SMT Divergence", eur_highs.index[-1]))

    return signal_log

# 📊 Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("EUR/USD (60min)")
    if eurusd.empty:
        st.warning("⚠️ Could not fetch EUR/USD data.")
    else:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=eurusd.index, y=eurusd["EURUSD=X"], mode='lines+markers', name="EUR/USD"))
        fig1.update_layout(
            margin=dict(t=10, b=10),
            xaxis_title="Time",
            yaxis_title="EUR/USD"
        )
        fig1.update_yaxes(tickformat=".4f")
        st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("DXY (60min)")
    if dxy.empty:
        st.warning("⚠️ Could not fetch DXY data.")
    else:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=dxy.index, y=dxy["DX-Y.NYB"], mode='lines+markers', name="DXY"))
        fig2.update_layout(
            margin=dict(t=10, b=10),
            xaxis_title="Time",
            yaxis_title="DXY"
        )
        fig2.update_yaxes(tickformat=".2f")
        st.plotly_chart(fig2, use_container_width=True)

# 📌 SMT Signals Panel
st.subheader("📌 SMT Divergence Signals")
signals = detect_smt_divergence(eurusd, dxy)

if not signals:
    st.info("No SMT divergence detected in the most recent data.")
else:
    for signal_type, signal_time in signals:
        st.success(f"{signal_type} detected at {signal_time.strftime('%Y-%m-%d %H:%M')}")
