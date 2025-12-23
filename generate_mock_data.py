import pandas as pd
from datetime import datetime, timedelta
import random
import os

# Create output folder
os.makedirs("mock_data", exist_ok=True)

# -----------------------------
# 1️⃣ team_registry
# -----------------------------
team_registry = pd.DataFrame({
    "team_id": ["T01","T02","T03","T04"],
    "team_name": ["UI Team", "DE Team", "Analytics Team", "Management Team"],
    "monthly_budget_usd": [5000,10000,8000,12000],
    "is_active": [True]*4,
    "created_at": [datetime(2025,12,1)]*4
})
team_registry.to_csv("mock_data/team_registry.csv", index=False)

# -----------------------------
# 2️⃣ user_registry
# -----------------------------
user_registry = pd.DataFrame({
    "user_id": ["U01","U02","U03","U04","U05","U06","U07","U08"],
    "user_name": ["Alice","Bob","Charlie","Dana","Eve","Frank","Grace","Henry"],
    "team_id": ["T01","T01","T02","T02","T03","T03","T04","T04"],
    "role": ["Engineer","Analyst","Engineer","Analyst","Data Analyst","Data Engineer","Manager","Manager"],
    "is_active": [True]*8
})
user_registry.to_csv("mock_data/user_registry.csv", index=False)

# -----------------------------
# 3️⃣ dataset_registry
# -----------------------------
dataset_registry = pd.DataFrame({
    "dataset_id": ["D01","D02","D03","D04"],
    "dataset_name": ["User_Events","Product_Analytics","Sales_Data","Dashboard_Reporting"],
    "size_gb": [500,800,1200,600],
    "is_partitioned": [True,False,False,True],
    "owner_team_id": ["T01","T02","T03","T04"]
})
dataset_registry.to_csv("mock_data/dataset_registry.csv", index=False)

# -----------------------------
# 4️⃣ query_usage_log
# -----------------------------
query_ids = [f"Q{str(i).zfill(2)}" for i in range(1,21)]
users = user_registry["user_id"].tolist()
datasets = dataset_registry["dataset_id"].tolist()
query_types = ["ad_hoc","dashboard","scheduled"]
query_origin = ["Looker","Notebook","API"]

query_usage_log = pd.DataFrame({
    "query_id": query_ids,
    "user_id": [random.choice(users) for _ in query_ids],
    "dataset_id": [random.choice(datasets) for _ in query_ids],
    "bytes_processed_gb": [random.randint(50,400) for _ in query_ids],
    "query_type": [random.choice(query_types) for _ in query_ids],
    "executed_at": [datetime(2025,12,10,8,0,0) + timedelta(hours=i*2) for i in range(len(query_ids))],
    "query_origin": [random.choice(query_origin) for _ in query_ids]
})
query_usage_log.to_csv("mock_data/query_usage_log.csv", index=False)

# -----------------------------
# 5️⃣ cost_model
# -----------------------------
cost_model = pd.DataFrame({
    "cost_per_gb_usd": [0.02],
    "partition_discount_factor": [0.8],
    "full_scan_penalty_factor": [1.5]
})
cost_model.to_csv("mock_data/cost_model.csv", index=False)

# -----------------------------
# 6️⃣ cost_attribution (derived)
# -----------------------------
cost_attrib_list = []
for idx, row in query_usage_log.iterrows():
    dataset = dataset_registry.loc[dataset_registry.dataset_id==row.dataset_id].iloc[0]
    base_cost = row.bytes_processed_gb * cost_model["cost_per_gb_usd"].iloc[0]
    if dataset.is_partitioned:
        cost = base_cost * cost_model["partition_discount_factor"].iloc[0]
        driver = "partition_discount"
    else:
        cost = base_cost * cost_model["full_scan_penalty_factor"].iloc[0]
        driver = "full_scan_penalty"
    team_id = user_registry.loc[user_registry.user_id==row.user_id,"team_id"].iloc[0]
    cost_attrib_list.append({
        "query_id": row.query_id,
        "team_id": team_id,
        "user_id": row.user_id,
        "calculated_cost_usd": round(cost,2),
        "cost_driver": driver,
        "cost_date": row.executed_at.date()
    })

cost_attribution = pd.DataFrame(cost_attrib_list)
cost_attribution.to_csv("mock_data/cost_attribution.csv", index=False)

# -----------------------------
# 7️⃣ budget_alerts (derived)
# -----------------------------
budget_alerts_list = []
for team in team_registry.itertuples():
    team_cost = cost_attribution.loc[cost_attribution.team_id==team.team_id,"calculated_cost_usd"].sum()
    if team_cost >= team.monthly_budget_usd:
        alert_type = "BREACH"
        threshold_pct = 100
    elif team_cost >= team.monthly_budget_usd*0.8:
        alert_type = "WARNING"
        threshold_pct = 80
    else:
        continue
    budget_alerts_list.append({
        "team_id": team.team_id,
        "alert_type": alert_type,
        "threshold_pct": threshold_pct,
        "triggered_at": datetime.now(),
        "status": "open"
    })
budget_alerts = pd.DataFrame(budget_alerts_list)
budget_alerts.to_csv("mock_data/budget_alerts.csv", index=False)

# -----------------------------
# 8️⃣ cost_trends (derived)
# -----------------------------
cost_trends_list = []
for team in team_registry.itertuples():
    team_costs = cost_attribution.loc[cost_attribution.team_id==team.team_id]
    for date, grp in team_costs.groupby("cost_date"):
        daily_cost = grp["calculated_cost_usd"].sum()
        trend = "up" if daily_cost >= 0 else "flat"  # simple placeholder
        cost_trends_list.append({
            "team_id": team.team_id,
            "date": date,
            "daily_cost_usd": round(daily_cost,2),
            "trend_direction": trend
        })
cost_trends = pd.DataFrame(cost_trends_list)
cost_trends.to_csv("mock_data/cost_trends.csv", index=False)

print("✅ All mock CSVs generated in ./mock_data/")
