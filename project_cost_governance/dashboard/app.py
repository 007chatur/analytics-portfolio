import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Cost Governance Dashboard", layout="wide")
st.markdown("<style>body {background-color: #000000; color: #fff;}</style>", unsafe_allow_html=True)

# -----------------------------
# Load data
# -----------------------------
user_registry = pd.read_csv("/Users/deadpool/analytics-platform-portfolio/project_cost_governance/data/user_registry.csv")
team_registry = pd.read_csv("/Users/deadpool/analytics-platform-portfolio/project_cost_governance/data/team_registry.csv")
query_usage_log = pd.read_csv("/Users/deadpool/analytics-platform-portfolio/project_cost_governance/data/query_usage_log.csv", parse_dates=["event_date"])
cost_attribution = pd.read_csv("/Users/deadpool/analytics-platform-portfolio/project_cost_governance/data/cost_attribution.csv", parse_dates=["cost_date"])
#budget_alerts = pd.read_csv("/Users/deadpool/analytics-platform-portfolio/project_cost_governance/data/budget_alerts.csv", parse_dates=["triggered_at"])

# -----------------------------
# Compute KPI values
# -----------------------------
total_users = user_registry[user_registry.is_active].shape[0]
total_teams = team_registry[team_registry.is_active].shape[0]

today = pd.Timestamp.today().normalize()
queries_today = query_usage_log[query_usage_log.event_date == today].shape[0]

daily_cost = cost_attribution[cost_attribution.cost_date == today]["calculated_cost_usd"].sum()
monthly_cost = cost_attribution[cost_attribution.cost_date.dt.month == today.month]["calculated_cost_usd"].sum()

#   open_alerts = budget_alerts[budget_alerts.status=="open"].shape[0]

# -----------------------------
# KPI list for rendering
# -----------------------------
kpis = [
    {"title":"Users Monitored","value":total_users,"trend":{"direction":"up","text":"Active users"},"is_currency":False},
    {"title":"Teams Monitored","value":total_teams,"trend":{"direction":"up","text":"All teams active"},"is_currency":False},
    {"title":"Queries Today","value":queries_today,"trend":{"direction":"up","text":"Δ since yesterday"},"is_currency":False},
    {"title":"Daily Cost","value":daily_cost,"trend":{"direction":"up","text":"Δ since yesterday"},"is_currency":True},
    {"title":"Monthly Cost","value":monthly_cost,"trend":{"direction":"up","text":"Δ since last month"},"is_currency":True}
    #{"title":"Budget Alerts","value":open_alerts,"trend":{"direction":"down","text":"Open alerts"},"is_currency":False}
]

# -----------------------------
# Render KPIs
# -----------------------------
st.markdown("<h2 style='color:#fff;'>Cost Governance KPIs</h2>", unsafe_allow_html=True)
cols = st.columns(len(kpis))

for idx, kpi in enumerate(kpis):
    value = f"${kpi['value']:,.2f}" if kpi.get("is_currency") else kpi["value"]
    arrow_color = "#00ff7f" if kpi["trend"]["direction"]=="up" else "#ff4500"
    arrow_symbol = "↑" if kpi["trend"]["direction"]=="up" else "↓"

    kpi_html = f"""
    <div style="
        background-color:#000000;
        color:white;
        padding:20px;
        border-radius:12px;
        text-align:center;
        margin-bottom:15px;
        border:1px solid #333;
        box-shadow:0 4px 6px rgba(0,0,0,0.3);
        font-family:sans-serif;
        width:180px;
        display:inline-block;">
        <div style="font-size:15px; color:#ccc; margin-bottom:5px;">{kpi['title']}</div>
        <div style="font-size:30px; font-weight:bold; color:#00ff7f;">{value}</div>
        <div style="color:{arrow_color}; font-size:13px; font-weight:bold; margin-top:4px;">
            {arrow_symbol} {kpi['trend']['text']}
        </div>
    </div>
    """
    cols[idx].markdown(kpi_html, unsafe_allow_html=True)
