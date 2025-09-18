# dashboard/pages/daily_oee.py
import streamlit as st
import pandas as pd
import mysql.connector
import plotly.graph_objects as go
from datetime import date

st.set_page_config(page_title="Daily OEE", layout="wide")

st.title("Casting Asakai Dashboard")
st.header("Daily OEE Trend")

# --- DB fetch helpers ---------------------------------------------------------
def fetch_df(sql, params=None):
    cn = mysql.connector.connect(host="db", user="root", password="secret", database="casting")
    df = pd.read_sql(sql, cn, params=params)
    cn.close()
    return df

# Get min/max to drive defaults
rng = fetch_df("SELECT MIN(report_date) AS min_d, MAX(report_date) AS max_d FROM v_daily_oee")
min_d, max_d = rng.loc[0, "min_d"], rng.loc[0, "max_d"]

if pd.isna(min_d) or pd.isna(max_d):
    st.info("No data yet.")
    st.stop()

# Sidebar controls
with st.sidebar:
    st.markdown("### streamlit app")
    st.checkbox("Show target line", value=True, key="show_target")
    target = st.slider("Target (%)", min_value=0, max_value=100, value=65, step=1)
    # default to full available range
    from_d = st.date_input("From", value=pd.to_datetime(min_d).date(), min_value=pd.to_datetime(min_d).date(), max_value=pd.to_datetime(max_d).date())
    to_d   = st.date_input("To",   value=pd.to_datetime(max_d).date(),  min_value=pd.to_datetime(min_d).date(), max_value=pd.to_datetime(max_d).date())

# Query data for range
sql = """
SELECT report_date,
       COALESCE(die_down_min,0)  AS die,
       COALESCE(mach_down_min,0) AS mach,
       COALESCE(eng_down_min,0)  AS eng,
       COALESCE(prod_down_min,0) AS prod,
       COALESCE(oth_down_min,0)  AS oth,
       oee_pct
FROM v_daily_oee
WHERE report_date BETWEEN %s AND %s
ORDER BY report_date
"""
df = fetch_df(sql, (from_d, to_d))

if df.empty:
    st.info("No data yet.")
    st.stop()

# Build chart
fig = go.Figure()

# Stacked bars = downtime categories
fig.add_bar(name="Die",     x=df["report_date"], y=df["die"])
fig.add_bar(name="Machine", x=df["report_date"], y=df["mach"])
fig.add_bar(name="Engineering", x=df["report_date"], y=df["eng"])
fig.add_bar(name="Production",  x=df["report_date"], y=df["prod"])
fig.add_bar(name="Others",  x=df["report_date"], y=df["oth"])

# OEE line on secondary axis, skip NaNs for the line but keep x positions
df_line = df.dropna(subset=["oee_pct"]).copy()
fig.add_trace(go.Scatter(
    name="OEE %",
    x=df_line["report_date"],
    y=df_line["oee_pct"],
    mode="lines+markers",
    yaxis="y2",
    line=dict(width=2),
    marker=dict(size=6)
))

# Add OEE labels (e.g., 56.8%) above each visible point
fig.add_trace(go.Scatter(
    x=df_line["report_date"],
    y=df_line["oee_pct"],
    text=[f"{v:.1f}%" for v in df_line["oee_pct"]],
    mode="text",
    textposition="top center",
    yaxis="y2",
    showlegend=False
))

# Optional dashed target
if st.session_state.get("show_target", True):
    fig.add_hline(y=target, line_dash="dash", line_color="red", opacity=0.6, yref="y2", name="Target")

# Layout
fig.update_layout(
    barmode="stack",
    xaxis=dict(title=None),
    yaxis=dict(title="Downtime (min)"),
    yaxis2=dict(title="OEE %", overlaying="y", side="right", range=[0, 100]),
    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="left", x=0),
    margin=dict(l=40, r=40, t=20, b=60),
    height=520,
)

st.plotly_chart(fig, use_container_width=True)
