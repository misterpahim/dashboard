# dashboard/pages/daily_oee.py
import streamlit as st
import pandas as pd
import mysql.connector
import plotly.graph_objects as go

st.set_page_config(page_title="Daily OEE Trend", layout="wide")
st.title("Daily OEE Trend")

@st.cache_data(ttl=60)
def load_data():
    conn = mysql.connector.connect(host="db", user="root", password="secret", database="casting")
    df = pd.read_sql("SELECT * FROM v_daily_oee ORDER BY report_date", conn)
    conn.close()
    return df

df = load_data()

if df.empty:
    st.info("No data yet. Run: `docker compose exec api python /app/ingest_oee.py`")
else:
    fig = go.Figure()
    fig.add_bar(name="Die",         x=df["report_date"], y=df["die_down_min"])
    fig.add_bar(name="Machine",     x=df["report_date"], y=df["mach_down_min"])
    fig.add_bar(name="Engineering", x=df["report_date"], y=df["eng_down_min"])
    fig.add_bar(name="Production",  x=df["report_date"], y=df["prod_down_min"])
    fig.add_bar(name="Others",      x=df["report_date"], y=df["oth_down_min"])

    fig.add_trace(go.Scatter(
        name="OEE %", x=df["report_date"], y=df["oee_pct"],
        mode="lines+markers", yaxis="y2"
    ))

    fig.update_layout(
        barmode="stack",
        yaxis=dict(title="Downtime (min)"),
        yaxis2=dict(title="OEE %", overlaying="y", side="right", range=[0,100]),
        legend=dict(orientation="h"),
        margin=dict(l=40, r=40, t=40, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)
