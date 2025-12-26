# scripts/generate_query_usage_log.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import uuid

# -------------------------
# CONFIGURATION
# -------------------------
MONTHS = 6
ENVIRONMENTS = ["prod", "staging", "dev"]

# usage multipliers by environment (prod dominates cost)
ENV_MULTIPLIER = {
    "prod": 1.0,
    "staging": 0.4,
    "dev": 0.25
}

# daily base usage volume for HIGH traffic
BASE_DAILY_QUERIES = 200   # average events across all users

# small randomness to make data feel alive, but not chaotic
VARIATION_SCALE = 0.3

random.seed(42)
np.random.seed(42)


# -------------------------
# LOAD DIMENSION DATA
# -------------------------
team_df = pd.read_csv("../data/team_registry.csv")
user_df = pd.read_csv("../data/user_registry.csv")
dataset_df = pd.read_csv("../data/dataset_registry.csv")


# -------------------------
# DATE RANGE (last 6 months)
# -------------------------
end_date = datetime.now().date()
start_date = end_date - timedelta(days=30 * MONTHS)
date_range = pd.date_range(start=start_date, end=end_date)


# -------------------------
# GENERATE HIGH USAGE EVENT SET
# -------------------------
events = []

for date in date_range:
    # usage spikes at month-end
    multiplier = 2.2 if date.day > 25 else 1.0

    num_queries_today = int(
        BASE_DAILY_QUERIES *
        np.random.normal(1, VARIATION_SCALE) *
        multiplier
    )

    for _ in range(max(1, num_queries_today)):
        user_row = user_df.sample(1).iloc[0]
        dataset_row = dataset_df.sample(1).iloc[0]
        environment = random.choices(
            ENVIRONMENTS,
            weights=[0.7, 0.2, 0.1],  # prod heavily used
            k=1
        )[0]

        # simulate cost relevance
        bytes_scanned = abs(np.random.normal(200, 80)) * ENV_MULTIPLIER[environment]

        events.append({
            "query_id": str(uuid.uuid4()),
            "event_date": date.strftime("%Y-%m-%d"),
            "user_id": user_row["user_id"],
            "team_id": user_row["team_id"],
            "dataset_id": dataset_row["dataset_id"],
            "environment": environment,
            "bytes_scanned_gb": round(bytes_scanned / 1024, 2),  # convert MB style to GB-ish
            "execution_time_ms": int(abs(np.random.normal(900, 300)))
        })


df = pd.DataFrame(events)
df.to_csv("../data/query_usage_log.csv", index=False)

print(f"Generated {len(df):,} high-usage events across {MONTHS} months 🚀")
