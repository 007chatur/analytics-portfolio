import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Cost Governance Dashboard", layout="wide")
st.markdown("<style>body {background-color: #000000; color: #fff;}</style>", unsafe_allow_html=True)

# ---------------------------------------------
# Load data
# ---------------------------------------------
user_registry = pd.read_csv("/Users/deadpool/analytics-platform-portfolio/project_cost_governance/data/user_registry.csv")
team_registry = pd.read_csv("/Users/deadpool/analytics-platform-portfolio/project_cost_governance/data/team_registry.csv")
query_usage_log = pd.read_csv("/Users/deadpool/analytics-platform-portfolio/project_cost_governance/data/query_usage_log.csv", parse_dates=["event_date"])
cost_attribution = pd.read_csv("/Users/deadpool/analytics-platform-portfolio/project_cost_governance/data/cost_attribution.csv", parse_dates=["cost_date"])


# ---------------------------------------------
# KPI calculations
# ---------------------------------------------
today = pd.Timestamp.today().normalize()
yesterday = today - timedelta(days=1)
last_7_days = today - timedelta(days=6)
last_30_days = today - timedelta(days=29)

# --- Core values ---
total_users = user_registry[user_registry.is_active].shape[0]
total_teams = team_registry[team_registry.is_active].shape[0]

queries_today = query_usage_log[query_usage_log.event_date == today].shape[0]
queries_yesterday = query_usage_log[query_usage_log.event_date == yesterday].shape[0]

today_cost = cost_attribution[cost_attribution.cost_date == today]["calculated_cost_usd"].sum()
yesterday_cost = cost_attribution[cost_attribution.cost_date == yesterday]["calculated_cost_usd"].sum()

# --- Avg daily cost (last 30 days incl today) ---
avg_daily_cost = (
    cost_attribution[cost_attribution.cost_date >= last_30_days]
    .groupby("cost_date")["calculated_cost_usd"].sum()
    .mean()
)

# --- Rolling 7-day avg ---
rolling_7d_avg_cost = (
    cost_attribution[cost_attribution.cost_date >= last_7_days]
    .groupby("cost_date")["calculated_cost_usd"].sum()
    .mean()
)

# --- Active users today ---
active_users_today = (
    query_usage_log[query_usage_log.event_date == today]["user_id"].nunique()
)

# --- Derived KPIs with safe handling ---
cost_per_query = today_cost / queries_today if queries_today > 0 else 0
queries_per_active_user = (
    queries_today / active_users_today if active_users_today > 0 else 0
)


# ---------------------------------------------
# Trend helper
# ---------------------------------------------
def trend_direction(current, previous):
    delta = current - previous
    direction = "up" if delta > 0 else "down"
    text = f"{delta:+,.2f} vs yesterday"
    return direction, text


# ---------------------------------------------
# KPI list for rendering
# ---------------------------------------------
kpis = [
    {"title": "Users Monitored", "value": total_users, "trend": {"direction":"up", "text":"Active"}, "is_currency": False},
    {"title": "Teams Monitored", "value": total_teams, "trend": {"direction":"up", "text":"Active"}, "is_currency": False},

    {"title": "Today's Queries", "value": queries_today,
     "trend": {"direction": trend_direction(queries_today, queries_yesterday)[0],
               "text": trend_direction(queries_today, queries_yesterday)[1]},
     "is_currency": False},

    {"title": "Today's Cost (USD)", "value": today_cost,
     "trend": {"direction": trend_direction(today_cost, yesterday_cost)[0],
               "text": trend_direction(today_cost, yesterday_cost)[1]},
     "is_currency": True},

    {"title": "Avg Daily Cost (30d)", "value": avg_daily_cost,
     "trend": {"direction":"up", "text":"Baseline avg"},
     "is_currency": True},

    {"title": "Cost per Query Today", "value": cost_per_query,
     "trend": {"direction":"up", "text":"Efficiency"},
     "is_currency": True},

    {"title": "Queries per Active User", "value": queries_per_active_user,
     "trend": {"direction":"up", "text":"Usage spread"},
     "is_currency": False},

    {"title": "Rolling 7d Avg Cost", "value": rolling_7d_avg_cost,
     "trend": {"direction":"up", "text":"Trailing avg"},
     "is_currency": True}
]


# ---------------------------------------------
# Render KPI cards
# ---------------------------------------------
st.markdown("<h2 style='color:#fff;'>Cost Governance KPIs</h2>", unsafe_allow_html=True)
#cols = st.columns(len(kpis))
# --- render KPIs in 2 rows ---
st.markdown("<h2 style='color:#fff;'>Cost Governance KPIs</h2>", unsafe_allow_html=True)

kpis_per_row = 4
num_rows = (len(kpis) + kpis_per_row - 1) // kpis_per_row

start = 0
for _ in range(num_rows):
    row_kpis = kpis[start:start + kpis_per_row]
    cols = st.columns(len(row_kpis))

    for idx, kpi in enumerate(row_kpis):
        arrow_symbol = "↑" if kpi["trend"]["direction"]=="up" else "↓"
        arrow_color = "#00ff7f" if kpi["trend"]["direction"]=="up" else "#ff4500"
        value = f"${kpi['value']:,.2f}" if kpi.get("is_currency") else kpi["value"]

        html = f"""
        <div style="
            background-color:#000000;
            color:white;
            padding:20px;
            border-radius:12px;
            border:1px solid #333;
            box-shadow:0 4px 6px rgba(0,0,0,0.3);
            text-align:center;
            font-family:sans-serif;
            width:180px;">
            <div style="font-size:15px; color:#ccc; margin-bottom:5px;">{kpi['title']}</div>
            <div style="font-size:30px; font-weight:bold; color:#00ff7f;">{value}</div>
            <div style="color:{arrow_color}; font-size:13px; font-weight:bold; margin-top:4px;">
                {arrow_symbol} {kpi['trend']['text']}
            </div>
        </div>
        """
        cols[idx].markdown(html, unsafe_allow_html=True)

    start += kpis_per_row



for idx, kpi in enumerate(kpis):
    arrow_symbol = "↑" if kpi["trend"]["direction"]=="up" else "↓"
    arrow_color = "#00ff7f" if kpi["trend"]["direction"]=="up" else "#ff4500"
    value = f"${kpi['value']:,.2f}" if kpi.get("is_currency") else kpi["value"]

    html = f"""
    <div style="
        background-color:#000000;
        color:white;
        padding:20px;
        border-radius:12px;
        border:1px solid #333;
        box-shadow:0 4px 6px rgba(0,0,0,0.3);
        text-align:center;
        font-family:sans-serif;
        width:180px;">
        <div style="font-size:15px; color:#ccc; margin-bottom:5px;">{kpi['title']}</div>
        <div style="font-size:30px; font-weight:bold; color:#00ff7f;">{value}</div>
        <div style="color:{arrow_color}; font-size:13px; font-weight:bold; margin-top:4px;">
            {arrow_symbol} {kpi['trend']['text']}
        </div>
    </div>
    """
    cols[idx].markdown(html, unsafe_allow_html=True)



# ---------------------------------------------
# TOP 5 COST DRIVERS — toggle view
# ---------------------------------------------
st.markdown("<h2 style='color:#fff; margin-top:30px;'>Top 5 Cost Drivers (7 days)</h2>", unsafe_allow_html=True)

# ---- Top 5 Cost Drivers ----
top_cost_drivers = (
    cost_attribution
    .groupby("cost_driver")["calculated_cost_usd"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .reset_index()
    .rename(columns={"cost_driver": "Cost Driver", "calculated_cost_usd": "Cost (USD)"})
)


view = st.radio(
    "View as:",
    ["Table", "Bar Chart"],
    horizontal=True,
    label_visibility="collapsed"
)

if view == "Table":
    st.dataframe(top_cost_drivers.reset_index().rename(columns={"dataset_id":"Dataset","calculated_cost_usd":"Cost (USD)"}))

else:
    st.bar_chart(top_cost_drivers)
