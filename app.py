import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="HDFC Bank Stock Analytics", page_icon="📈", layout="wide")

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "HDFCBANK_Stock_Data.csv"

st.markdown("""
<style>
:root { --page:#EDE6D8; --panel:#FBF8F1; --ink:#3E352D; --muted:#766B5E; --accent:#8A6F4D; }
.stApp { background: #EDE6D8; color: #3E352D; }
.block-container {padding-top: 1.15rem; padding-bottom: 2rem; max-width: 1600px;}
.hero {padding: 1.35rem 1.6rem; border-radius: 14px; background: linear-gradient(115deg,#E4D7C2 0%,#F8F4EA 72%,#D9C8AE 100%); color:#3E352D; border:1px solid #D4C5AF; margin-bottom:1rem; box-shadow:0 3px 12px rgba(72,55,35,.06);}
.hero h1 {color:#3E352D; margin:0; font-size:2rem; letter-spacing:-.02em;}
.hero p {color:#766B5E; margin:.4rem 0 0 0;}
div[data-testid="stMetric"] {background:#FBF8F1; border:1px solid #DCD1C0; padding:14px 16px; border-radius:12px; box-shadow:0 2px 7px rgba(72,55,35,.05);}
div[data-testid="stMetricLabel"] {color:#766B5E;}
div[data-testid="stMetricValue"] {color:#3E352D;}
[data-testid="stSidebar"] {background:#E5DACA; border-right:1px solid #D4C5AF;}
[data-testid="stTabs"] button {color:#5D5144;}
.stPlotlyChart, div[data-testid="stDataFrame"] {background:#FBF8F1; border:1px solid #DCD1C0; border-radius:12px; padding:5px;}
.small-note {color:#766B5E; font-size:.85rem;}
</style>
<div class="hero"><h1>HDFC Bank Stock Analytics Dashboard</h1><p>Intraday stock analysis · Five-minute OHLCV data · Trend lines · Moving averages · Volume · Returns</p></div>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")
    data = pd.read_csv(DATA_PATH)
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce", utc=True).dt.tz_convert("Asia/Kolkata")
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")
    data = data.dropna(subset=["Date", "Open", "High", "Low", "Close", "Volume"])
    data = data.sort_values("Date").drop_duplicates(subset=["Date"]).reset_index(drop=True)
    data["SessionDate"] = data["Date"].dt.date
    data["ReturnPct"] = data["Close"].pct_change() * 100
    data["MA20_Observations"] = data["Close"].rolling(20, min_periods=1).mean()
    data["MA50_Observations"] = data["Close"].rolling(50, min_periods=1).mean()
    return data

try:
    data = load_data()
except Exception as exc:
    st.error(f"Could not load the stock dataset. {exc}")
    st.stop()

min_day, max_day = data["SessionDate"].min(), data["SessionDate"].max()
st.sidebar.header("Dashboard filters")
st.sidebar.caption("Filter the historical intraday observations by trading date.")
selected_dates = st.sidebar.date_input("Select date range", value=(min_day, max_day), min_value=min_day, max_value=max_day)
if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
    start_day, end_day = selected_dates
else:
    start_day = end_day = selected_dates
filtered = data[(data["SessionDate"] >= start_day) & (data["SessionDate"] <= end_day)].copy()
if filtered.empty:
    st.warning("No observations exist in this date range. Choose another range in the sidebar.")
    st.stop()

latest = filtered.iloc[-1]
first_close = filtered.iloc[0]["Close"]
last_close = filtered.iloc[-1]["Close"]
period_change = ((last_close / first_close) - 1) * 100 if first_close else np.nan
high_value = filtered["High"].max()
low_value = filtered["Low"].min()
volume_total = filtered["Volume"].sum()

m1,m2,m3,m4,m5 = st.columns(5)
m1.metric("Latest close", f"₹{last_close:,.2f}", f"{period_change:+.2f}% over selection")
m2.metric("Highest price", f"₹{high_value:,.2f}")
m3.metric("Lowest price", f"₹{low_value:,.2f}")
m4.metric("Total volume", f"{volume_total:,.0f}")
m5.metric("Observations", f"{len(filtered):,}")

st.caption(f"Showing {len(filtered):,} five-minute observations from {pd.Timestamp(start_day):%d %b %Y} to {pd.Timestamp(end_day):%d %b %Y}. Prices are in INR. Historical analysis only — not investment advice.")

# Plotly charts share a consistent, light corporate style.
layout_common = dict(template="plotly_white", paper_bgcolor="#FBF8F1", plot_bgcolor="#FBF8F1", font=dict(family="Arial, sans-serif", color="#3E352D", size=12), margin=dict(l=20,r=20,t=55,b=20), hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(color="#5D5144")), xaxis=dict(gridcolor="#E8E0D3", zerolinecolor="#D8CCBA"), yaxis=dict(gridcolor="#E8E0D3", zerolinecolor="#D8CCBA"))

st.subheader("Price movement and trend")
price_tab, trend_tab = st.tabs(["Closing price", "Trend line and channel"])
with price_tab:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=filtered["Date"], y=filtered["Close"], name="Close", mode="lines", line=dict(color="#668F7A", width=2)))
    fig.add_trace(go.Scatter(x=filtered["Date"], y=filtered["MA20_Observations"], name="20-observation average", mode="lines", line=dict(color="#A65D57", width=1.6)))
    fig.add_trace(go.Scatter(x=filtered["Date"], y=filtered["MA50_Observations"], name="50-observation average", mode="lines", line=dict(color="#8A6F4D", width=1.6)))
    fig.update_layout(title="HDFC Bank closing price and rolling averages", yaxis_title="Price (₹)", xaxis_title="Timestamp", **layout_common)
    st.plotly_chart(fig, use_container_width=True)
with trend_tab:
    if len(filtered) >= 2:
        x = np.arange(len(filtered), dtype=float)
        y = filtered["Close"].to_numpy(dtype=float)
        slope, intercept = np.polyfit(x, y, 1)
        trend = slope*x + intercept
        residuals = y-trend
        upper = trend + np.nanmax(residuals)
        lower = trend + np.nanmin(residuals)
        trend_fig = go.Figure()
        trend_fig.add_trace(go.Scatter(x=filtered["Date"], y=y, name="Close", mode="lines", line=dict(color="#668F7A", width=1.7)))
        trend_fig.add_trace(go.Scatter(x=filtered["Date"], y=trend, name="Linear trend", mode="lines", line=dict(color="#A65D57", dash="dash", width=2)))
        trend_fig.add_trace(go.Scatter(x=filtered["Date"], y=upper, name="Upper residual boundary", mode="lines", line=dict(color="#668F7A", dash="dot", width=1.3)))
        trend_fig.add_trace(go.Scatter(x=filtered["Date"], y=lower, name="Lower residual boundary", mode="lines", line=dict(color="#B99A70", dash="dot", width=1.3), fill="tonexty", fillcolor="rgba(185,154,112,.10)"))
        trend_fig.update_layout(title="Linear trend with residual boundaries", yaxis_title="Price (₹)", xaxis_title="Timestamp", **layout_common)
        st.plotly_chart(trend_fig, use_container_width=True)
        direction = "upward" if slope > 0 else "downward" if slope < 0 else "flat"
        st.info(f"The fitted line has a {direction} slope of approximately ₹{slope:.4f} per observation. These boundaries describe observed residual extremes; they are descriptive, not a forecast or a statistical confidence interval.")
    else:
        st.info("Select at least two observations to calculate a trend line.")

left, right = st.columns(2)
with left:
    st.subheader("High and low price by session")
    daily = filtered.groupby("SessionDate", as_index=False).agg(High=("High","max"), Low=("Low","min"), Close=("Close","last"), Open=("Open","first"), Volume=("Volume","sum"))
    f = go.Figure()
    f.add_trace(go.Scatter(x=daily["SessionDate"], y=daily["High"], name="Session high", mode="lines+markers", line=dict(color="#668F7A")))
    f.add_trace(go.Scatter(x=daily["SessionDate"], y=daily["Low"], name="Session low", mode="lines+markers", line=dict(color="#8A6F4D")))
    f.update_layout(title="Maximum high vs minimum low", yaxis_title="Price (₹)", xaxis_title="Session date", **layout_common)
    st.plotly_chart(f, use_container_width=True)
with right:
    st.subheader("Trading volume by session")
    vol_fig=px.bar(daily, x="SessionDate", y="Volume", title="Total recorded volume per session", labels={"SessionDate":"Session date","Volume":"Volume"}, color_discrete_sequence=["#668F7A"])
    vol_fig.update_layout(**layout_common)
    st.plotly_chart(vol_fig, use_container_width=True)

left2, right2 = st.columns(2)
with left2:
    st.subheader("Five-minute return distribution")
    ret = filtered["ReturnPct"].dropna()
    if not ret.empty:
        ret_fig=px.histogram(ret, nbins=40, labels={"value":"Return (%)"}, title="Distribution of observation-to-observation returns", color_discrete_sequence=["#A65D57"])
        ret_fig.update_layout(**layout_common)
        st.plotly_chart(ret_fig, use_container_width=True)
    else:
        st.info("Not enough observations to calculate returns.")
with right2:
    st.subheader("Return over selected period")
    daily["DailyCloseReturnPct"] = daily["Close"].pct_change()*100
    daily_ret = daily.dropna(subset=["DailyCloseReturnPct"])
    if not daily_ret.empty:
        ret_fig2=px.bar(daily_ret, x="SessionDate", y="DailyCloseReturnPct", title="Close-to-close return between available sessions", labels={"SessionDate":"Session date","DailyCloseReturnPct":"Return (%)"}, color="DailyCloseReturnPct", color_continuous_scale=["#A65D57","#FBF8F1","#668F7A"])
        ret_fig2.update_layout(**layout_common, coloraxis_showscale=False)
        st.plotly_chart(ret_fig2, use_container_width=True)
    else:
        st.info("Select more than one session to compare close-to-close returns.")

with st.expander("Explore filtered data"):
    show_cols = ["Date","Open","High","Low","Close","Volume","ReturnPct","MA20_Observations","MA50_Observations"]
    st.dataframe(filtered[show_cols], use_container_width=True, hide_index=True)
    csv_bytes = filtered[show_cols].to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered observations (CSV)", data=csv_bytes, file_name="hdfcbank_filtered_observations.csv", mime="text/csv")

st.divider()
st.markdown("<p class='small-note'>Built with Python, Pandas, NumPy, Plotly and Streamlit. Power BI report file is included in the repository's <code>powerbi/</code> folder.</p>", unsafe_allow_html=True)
