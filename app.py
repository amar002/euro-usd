import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objs as go

st.set_page_config(page_title="ICT SMT Divergence Dashboard", layout="wide")
st.title("📊 ICT SMT Divergence Detector (EUR/USD vs DXY)")

# -------- Fetch & Clean Data --------
@st.cache_data(ttl=900)
def fetch_data(ticker: str):
    df = yf.download(ticker, period="5d", interval="60m", progress=False)
    df = df[['Close']].dropna().rename(columns={"Close": ticker})
    df.index = pd.to_datetime(df.index)
    return df

eurusd = fetch_data("EURUSD=X")
dxy = fetch_data("DX-Y.NYB")

# Align both on same timestamps
common_index = eurusd.index.intersection(dxy.index)
eurusd = eurusd.loc[common_index]
dxy = dxy.loc[common_index]

# -------- SMT Divergence Detection --------
def find_local_extrema(series, window=3):
    lows = (series.shift(1) > series) & (series.shift(-1) > series)
    highs = (series.shift(1) < series) & (series.shift(-1) < series)
    return series[lows], series[highs]

def detect_smt_divergence(eur_df, dxy_df):
    signal_log = []
    eur_lows, eur_highs = find_local_extrema(eur_df["EURUSD=X"])
    dxy_lows, dxy_highs = find_local_extrema(dxy_df["DX-Y.NYB"])

    if eur_lows.empty or eur_highs.empty or dxy_lows.empty or dxy_highs.empty:
        return signal_log
    if len(eur_lows) < 2 or len(eur_highs) < 2 or len(dxy_lows) < 2 or len(dxy_highs) < 2:
        return signal_log

    # Extract scalar values (no ambiguity errors)
    eur_low_recent = eur_lows.values[-1]
    eur_low_prev = eur_lows.values[-2]
    dxy_high_recent = dxy_highs.values[-1]
    dxy_high_prev = dxy_highs.values[-2]

    eur_high_recent = eur_highs.values[-1]
    eur_high_prev = eur_highs.values[-2]
    dxy_low_recent = dxy_lows.values[-1]
    dxy_low_prev = dxy_lows.values[-2]

    if eur_low_recent < eur_low_prev and dxy_high_recent < dxy_high_prev:
        signal_log.append(("Bullish SMT Divergence", eur_lows.index[-1]))

    if eur_high_recent > eur_high_prev and dxy_low_recent > dxy_low_prev:
        signal_log.append(("Bearish SMT Divergence", eur_highs.index[-1]))

    return signal_log

# -------- Plot Charts --------
col1, col2 = st.columns(2)

with col1:
    st.subheader("EUR/USD (60min)")
    if eurusd.shape[0] < 3:
        st.warning("⚠️ Not enough EUR/USD data points to plot.")
    else:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=eurusd.index,
            y=eurusd["EURUSD=X"],
            mode='lines+markers',
            name="EUR/USD",
            line=dict(color='cyan')
        ))
        fig1.update_layout(
            margin=dict(t=10, b=10),
            xaxis_title="Time",
            yaxis_title="EUR/USD",
            xaxis=dict(tickformat="%b %d %H:%M")
        )
        fig1.update_yaxes(tickformat=".4f")
        st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("DXY (60min)")
    if dxy.shape[0] < 3:
        st.warning("⚠️ Not enough DXY data points to plot.")
    else:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=dxy.index,
            y=dxy["DX-Y.NYB"],
            mode='lines+markers',
            name="DXY",
            line=dict(color='orange')
        ))
        fig2.update_layout(
            margin=dict(t=10, b=10),
            xaxis_title="Time",
            yaxis_title="DXY",
            xaxis=dict(tickformat="%b %d %H:%M")
        )
        fig2.update_yaxes(tickformat=".2f")
        st.plotly_chart(fig2, use_container_width=True)

# -------- SMT Signal Output --------
st.subheader("📌 SMT Divergence Signals")
signals = detect_smt_divergence(eurusd, dxy)

if not signals:
    st.info("No SMT divergence detected in the most recent data.")
else:
    for signal_type, signal_time in signals:
        st.success(f"{signal_type} detected at {signal_time.strftime('%Y-%m-%d %H:%M')}")
