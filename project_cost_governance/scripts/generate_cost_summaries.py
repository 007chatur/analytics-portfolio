import pandas as pd
import os

DATA_DIR = "/Users/deadpool/analytics-platform-portfolio/project_cost_governance/data"
OUTPUT_DIR = "/Users/deadpool/analytics-platform-portfolio/project_cost_governance/data/derived"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_data():
    team_registry = pd.read_csv(f"{DATA_DIR}/team_registry.csv")
    user_registry = pd.read_csv(f"{DATA_DIR}/user_registry.csv")
    dataset_registry = pd.read_csv(f"{DATA_DIR}/dataset_registry.csv")
    cost_attribution = pd.read_csv(f"{DATA_DIR}/cost_attribution.csv")
    cost_trends = pd.read_csv(f"{DATA_DIR}/cost_trends.csv")

    return team_registry, user_registry, dataset_registry, cost_attribution, cost_trends


def generate_team_cost_summary(cost_attribution, team_registry):
    team_costs = (
        cost_attribution.groupby("team_id")["calculated_cost_usd"]
        .sum()
        .reset_index()
        .rename(columns={"calculated_cost_usd": "total_cost_usd"})
    )

    merged = team_costs.merge(team_registry[["team_id", "team_name", "monthly_budget_usd"]], on="team_id")

    merged["budget_usage_pct"] = round((merged["total_cost_usd"] / merged["monthly_budget_usd"]) * 100, 2)
    merged["budget_status"] = merged["budget_usage_pct"].apply(
        lambda x: "BREACH" if x >= 100 else ("WARNING" if x >= 80 else "NORMAL")
    )

    merged.to_csv(f"{OUTPUT_DIR}/team_cost_summary.csv", index=False)
    print("✓ team_cost_summary.csv written")

    return merged


def generate_user_cost_summary(cost_attribution, user_registry):
    user_costs = (
        cost_attribution.groupby(["user_id"])["calculated_cost_usd"]
        .sum()
        .reset_index()
        .rename(columns={"calculated_cost_usd": "total_cost_usd"})
    )

    merged = user_costs.merge(user_registry[["user_id", "user_name", "team_id"]], on="user_id")

    merged.to_csv(f"{OUTPUT_DIR}/user_cost_summary.csv", index=False)
    print("✓ user_cost_summary.csv written")

    return merged


def generate_dataset_cost_summary(cost_attribution, dataset_registry):
    dataset_costs = (
        cost_attribution.groupby("dataset_id")["calculated_cost_usd"]
        .sum()
        .reset_index()
        .rename(columns={"calculated_cost_usd": "total_cost_usd"})
    )

    merged = dataset_costs.merge(dataset_registry[["dataset_id", "dataset_name"]], on="dataset_id")

    merged.to_csv(f"{OUTPUT_DIR}/dataset_cost_summary.csv", index=False)
    print("✓ dataset_cost_summary.csv written")

    return merged

# ---------------------------------------------------------
# NEW SUMMARY #3 — DAILY COST TREND
# ---------------------------------------------------------
def generate_daily_cost_summary(cost_attribution: pd.DataFrame, output_dir: str):
    print(" → Generating daily cost summary...")

    # Ensure date is parsed (string → date)
    cost_attribution["cost_date"] = pd.to_datetime(cost_attribution["cost_date"])

    daily_summary = (
        cost_attribution
        .groupby(cost_attribution["cost_date"].dt.date)["calculated_cost_usd"]
        .sum()
        .reset_index()
        .rename(columns={
            "cost_date": "date",
            "calculated_cost_usd": "total_cost_usd"
        })
    )


    out_path = os.path.join(OUTPUT_DIR, "daily_cost_summary.csv")
    daily_summary.to_csv(out_path, index=False)
    print(f" ✓ daily_cost_summary.csv written")


# ---------------------------------------------------------
# NEW SUMMARY #4 — COST BY DRIVER
# ---------------------------------------------------------
def generate_driver_cost_summary(cost_attribution: pd.DataFrame, output_dir: str):
    print(" → Generating driver cost summary...")

    driver_summary = (
        cost_attribution
        .groupby("cost_driver")["calculated_cost_usd"]
        .sum()
        .reset_index()
        .rename(columns={"calculated_cost_usd": "total_cost_usd"})
    )
    
    
    out_path = os.path.join(OUTPUT_DIR, "driver_cost_summary.csv")
    driver_summary.to_csv(out_path, index=False)
    print(f" ✓ driver_cost_summary.csv written")


if __name__ == "__main__":
    team_registry, user_registry, dataset_registry, cost_attribution, cost_trends = load_data()
    
    print("\n🚀 Generating derived cost summaries ...\n")

    generate_team_cost_summary(cost_attribution, team_registry)
    generate_user_cost_summary(cost_attribution, user_registry)
    generate_daily_cost_summary(cost_attribution, OUTPUT_DIR)
    generate_driver_cost_summary(cost_attribution, OUTPUT_DIR)

    print("\n🎉 Done — summaries generated under project_cost_governance/data/derived/\n")
