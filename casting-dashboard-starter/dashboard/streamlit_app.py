
import os, pandas as pd, requests, streamlit as st
from datetime import date, timedelta
st.set_page_config(page_title="Casting Asakai", layout="wide")
st.title("Casting Asakai Dashboard")
show_target = st.sidebar.checkbox("Show target line", True)
target_val = st.sidebar.slider("Target (%)", 0, 100, 65)
today = date.today()
start = st.sidebar.date_input("From", today - timedelta(days=30))
end = st.sidebar.date_input("To", today)
API_BASE = os.environ.get("API_BASE", "http://localhost:8000")
try:
    r = requests.get(f"{API_BASE}/kpi/efficiency", params={"date_from":start, "date_to":end}, timeout=10)
    data = pd.DataFrame(r.json())
except Exception:
    data = pd.DataFrame(columns=["report_date","sheet_name","metric_value"])
if not data.empty:
    data["report_date"] = pd.to_datetime(data["report_date"])
    data["oee_pct"] = (data["metric_value"]*100).round(1)
st.subheader("Daily OEE Trend")
if data.empty:
    st.info("No data yet.")
else:
    oee = data.groupby("report_date", as_index=False)["oee_pct"].mean()
    st.line_chart(oee.set_index("report_date")["oee_pct"], height=300, use_container_width=True)
    if show_target:
        st.caption(f"Target: {target_val}%")
