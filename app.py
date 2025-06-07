import numpy as np

# Utility to find local highs/lows
def find_local_extrema(series, window=3):
    lows = (series.shift(1) > series) & (series.shift(-1) > series)
    highs = (series.shift(1) < series) & (series.shift(-1) < series)
    return series[lows], series[highs]

# Detect SMT Divergence between EUR/USD and DXY
def detect_smt_divergence(eur_df, dxy_df):
    signal_log = []

    eur_lows, eur_highs = find_local_extrema(eur_df["EURUSD=X"])
    dxy_lows, dxy_highs = find_local_extrema(dxy_df["DX-Y.NYB"])

    if len(eur_lows) < 2 or len(eur_highs) < 2 or len(dxy_lows) < 2 or len(dxy_highs) < 2:
        return signal_log  # not enough data

    # Get most recent two lows/highs
    eur_low_recent = eur_lows.iloc[-1]
    eur_low_prev = eur_lows.iloc[-2]
    dxy_high_recent = dxy_highs.iloc[-1]
    dxy_high_prev = dxy_highs.iloc[-2]

    eur_high_recent = eur_highs.iloc[-1]
    eur_high_prev = eur_highs.iloc[-2]
    dxy_low_recent = dxy_lows.iloc[-1]
    dxy_low_prev = dxy_lows.iloc[-2]

    # Bullish Divergence
    if eur_low_recent < eur_low_prev and dxy_high_recent < dxy_high_prev:
        signal_log.append(("Bullish SMT Divergence", eur_lows.index[-1]))

    # Bearish Divergence
    if eur_high_recent > eur_high_prev and dxy_low_recent > dxy_low_prev:
        signal_log.append(("Bearish SMT Divergence", eur_highs.index[-1]))

    return signal_log
