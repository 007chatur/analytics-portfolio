import streamlit as st
from pathlib import Path
import pandas as pd
from datetime import datetime
import uuid


#Lower-level objects must exist before higher-level ones.
RESOURCE_PRIORITY = {
    "user": 1,
    "group": 2,
    "role": 3,
    "model": 4,
    "dataset": 5
}


st.set_page_config(page_title="Analytics Platform Portfolio", layout="wide")

st.title("👋 Hi, I'm Shuvam a Senior Analytics Engineer")

st.markdown("""
I build and operate scalable analytics platforms using cloud-native tools.
This portfolio highlights my experience across data engineering, analytics
engineering, and platform orchestration.
""")

st.divider()

st.header("🔧 Tech Stack")
st.markdown("""
- Python, SQL  
- Airflow / Cloud Composer  
- BigQuery, Snowflake  
- GCP  
- Looker / LookML  
- GitHub Actions, Webhooks  
- Agile delivery
""")

st.divider()

st.header("📊 Projects")

st.subheader("1. Airflow Orchestration Framework")
st.markdown("""
A standardized DAG framework for managing dependencies, retries, and monitoring
across analytics pipelines.
""")

st.subheader("2. BI Access & Governance Automation")
st.markdown("""
Automation for Looker users, groups, roles, and permissions using Python and APIs.
""")

st.divider()

st.header("Project 1: Metadata-Driven Analytics Control Plane")

st.divider()


st.markdown("""
This project demonstrates a **metadata-driven control plane** used to manage
analytics resources, access relationships, and execution governance at scale.

🔹 The architecture is **tool-agnostic by design**  
🔹 Looker is used as a **reference implementation**  
🔹 The same pattern applies to Snowflake, dbt, Tableau, Power BI, or internal tools
""")

BASE_PATH = Path("control_tables")

def load_csv(filename):
    return pd.read_csv(BASE_PATH / filename)

# -------------------------
# Tabs
# -------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🧱 Resource Registry",
    "🔗 Relationship Registry",
    "🌍 Environment Config",
    "🧾 Execution Audit"
])

# -------------------------
# Resource Registry
# -------------------------
with tab1:
    st.subheader("🧱 Resource Registry")
    st.markdown("""
    **Purpose:**  
    Defines *what resources should exist* across applications and environments.

    This table is **generic by design**.  
    It supports users, groups, roles, datasets, pipelines, dashboards — without schema changes.
    """)

    df_resources = load_csv("resource_registry.csv")
    st.dataframe(df_resources, use_container_width=True)

    st.info("""
    💡 Think of this as the **source of truth for existence**.
    No execution logic lives here.
    """)

# -------------------------
# Relationship Registry
# -------------------------
with tab2:
    st.subheader("🔗 Relationship Registry")
    st.markdown("""
    **Purpose:**  
    Defines *how resources relate to each other*.

    This single table supports:
    - user → group membership
    - group → role assignment
    - dataset → consumer access
    - dashboard → group visibility
    """)

    df_relationships = load_csv("relationship_registry.csv")
    st.dataframe(df_relationships, use_container_width=True)

    st.info("""
    💡 This is a **polymorphic relationship model**.
    Meaning is interpreted by adapters, not the control plane.
    """)

# -------------------------
# Environment Config
# -------------------------
with tab3:
    st.subheader("🌍 Environment Configuration")
    st.markdown("""
    **Purpose:**  
    Enforces safety and governance rules per environment.

    This prevents:
    - accidental prod deletes
    - unsafe executions
    - unapproved changes
    """)

    df_env = load_csv("environment_config.csv")
    st.dataframe(df_env, use_container_width=True)

    st.warning("""
    ⚠️ Notice how **prod runs in dry-run mode**.
    This is a deliberate governance choice.
    """)

# -------------------------
# Execution Audit
# -------------------------
with tab4:
    st.subheader("🧾 Execution Audit")
    st.markdown("""
    **Purpose:**  
    Records *what the system attempted to execute* and the outcome.

    This table starts empty and is populated by the orchestrator.
    """)

    df_audit = load_csv("execution_audit.csv")
    st.dataframe(df_audit, use_container_width=True)

    st.info("""
    💡 Auditing enables debugging, retries, and trust in automation.
    """)


st.markdown("### 🏗️ Architecture Note")

st.expander("""
This application models a declarative control plane.

Registry tables define the intended configuration of resources and relationships.
Execution planners reconcile these registries against the current system state
to generate safe, idempotent actions suitable for orchestration (e.g., Airflow DAGs).
""")


# -------------------------
# Simulated current state
# -------------------------
CURRENT_STATE = {
    "user": ["alice"],
    "group": ["finance_analysts"],
    "role": [],
    "model": [],
    "dataset": ["finance_dataset"]
}

#This method takes the above defined  CURRENT_STATE dictionary as a parameter and converts it to "Current System State (Observed)" table in application
def build_current_state_df(current_state):
    rows = []
    for resource_type, names in current_state.items():
        for name in names:
            rows.append({
                "resource_type": resource_type,
                "resource_name": name,
                "state": "🟢 EXISTS"
            })
    return pd.DataFrame(rows)

def resource_exists(resource_type, resource_name):
    return resource_name in CURRENT_STATE.get(resource_type, [])

def relationship_exists(relationship_type, source_name, target_name):
    existing = CURRENT_RELATIONSHIPS.get(relationship_type, [])
    return (source_name, target_name) in existing

# -------------------------
# Simulated current relationships
# -------------------------
CURRENT_RELATIONSHIPS = {
    "user_to_group": [("alice", "finance_analysts")],
    "group_to_role": [],
    "role_to_model": [],
    "model_to_dataset": []
}

#This method takes the above defined  CURRENT_STATE dictionary as a parameter and converts it to "Current Relationship State" table in application
def current_relationships_df():
    rows = []

    for rel_type, pairs in CURRENT_RELATIONSHIPS.items():
        for source, target in pairs:
            rows.append({
                "relationship_type": rel_type,
                "source": source,
                "target": target,
                "state": "🟢 EXISTS"
            })

    return pd.DataFrame(rows)



st.divider()
st.subheader("🔍 Current System State (Observed)")

st.markdown("""
This section represents the **observed state of the system**  
(before any execution planning).

⚠️ For demo purposes, this state is **simulated**.
In a real system, this would come from APIs or metadata scans.
""")

current_state_df = build_current_state_df(CURRENT_STATE)
st.dataframe(
    current_state_df,
    use_container_width=True,
    hide_index=True
)


def generate_execution_plan(resources_df, env_config_df, environment):
    plan = []

    env_row = env_config_df[env_config_df["environment"] == environment].iloc[0]
    execution_mode = env_row["execution_mode"]

    for _, row in resources_df.iterrows():
        if not row["is_active"]:
            continue

        resource_type = row["resource_type"]
        resource_name = row["resource_name"]

        exists = resource_name in CURRENT_STATE.get(resource_type, [])

        if not exists:
            action = "CREATE"
        else:
            action = "NO_OP"
        priority = RESOURCE_PRIORITY.get(resource_type, 99)
        plan.append({
            "resource_type"  :  resource_type,
            "resource_name"  : resource_name,
            "planned_action" : action,
            "execution_mode" : execution_mode,
            "priority"       : priority

        })

    return pd.DataFrame(plan)

st.divider()
st.subheader("⚙️ Execution Planner (Dry Run)")

environment = st.selectbox(
    "Select Environment",
    options=df_env["environment"].unique()
)

execution_plan = generate_execution_plan(
    df_resources,
    df_env,
    environment
)

st.dataframe(execution_plan, use_container_width=True)

st.info("""
This is a **dry-run execution plan**.
No changes are applied to any system.
""")

st.subheader("🔗 Current Relationship State")

current_rel_df = current_relationships_df()

if current_rel_df.empty:
    st.warning("No relationships currently exist in the system.")
else:
    st.dataframe(
        current_rel_df,
        use_container_width=True,
        hide_index=True
    )

st.caption("""
Represents relationships that currently exist in the system
before any planning or execution.
""")

  
def generate_relationship_plan(relationships_df, resources_df):
    plan = []

    # Map resource_id → (type, name)
    resource_lookup = {
        row.resource_id: (row.resource_type, row.resource_name)
        for _, row in resources_df.iterrows()
    }

    for _, row in relationships_df.iterrows():
        if not row.is_active:
            continue

        rel_type = row.relationship_type

        source_type, source_name = resource_lookup[row.source_resource_id]
        target_type, target_name = resource_lookup[row.target_resource_id]

        # Step 1: Ensure both resources exist
        if not resource_exists(source_type, source_name):
            plan.append({
                "object": source_name,
                "action": "CREATE_RESOURCE",
                "details": f"{source_type} missing",
                "priority": 100

            })
            continue

        if not resource_exists(target_type, target_name):
            plan.append({
                "object": target_name,
                "action": "CREATE_RESOURCE",
                "details": f"{target_type} missing",
                "priority": 100
            })
            continue

        # Step 2: Check relationship existence
        if relationship_exists(rel_type, source_name, target_name):
            action = "NO_OP"
            details = "relationship already exists"
        else:
            action = "ADD_RELATIONSHIP"
            details = f"{source_name} → {target_name}"

        plan.append({
            "object": rel_type,
            "action": action,
            "details": details,
            "priority": 100

        })

    return pd.DataFrame(plan)

st.divider()
st.subheader("🔗 Relationship Execution Plan")

relationship_plan = generate_relationship_plan(
    df_relationships,
    df_resources
)

st.dataframe(
    relationship_plan,
    use_container_width=True,
    hide_index=True
)

st.info("""
This plan ensures all required relationships exist
after resources are validated or created.
""")


def build_final_execution_plan(resource_plan_df, relationship_plan_df):
    final_plan = pd.concat(
        [resource_plan_df, relationship_plan_df],
        ignore_index=True,
        sort=False
    )

    final_plan = final_plan.sort_values("priority")
    return final_plan

final_execution_plan_df = build_final_execution_plan(
    execution_plan,
    relationship_plan
)
st.divider()
st.subheader("🚀 Final Execution Plan")

st.dataframe(
    final_execution_plan_df,
    use_container_width=True,
    hide_index=True
)

st.caption("""
Ordered execution plan combining resource-level and relationship-level actions.
Different action types are executed by different operators in a real DAG.
""")


def simulate_execution(final_execution_plan_df):
    audit_rows = []
    execution_id = str(uuid.uuid4())

    for _, row in final_execution_plan_df.iterrows():

        # determine status
        if row.get("planned_action") == "NO_OP":
            status = "SKIPPED"
        elif row.get("execution_mode") == "dry_run":
            status = "SKIPPED"
        else:
            status = "SUCCESS"

        audit_rows.append({
            "execution_id": execution_id,
            "resource_type": row.get("resource_type", "relationship"),
            "resource_name": row.get("resource_name", row.get("object")),
            "action": row.get("planned_action", row.get("action")),
            "status": status,
            "timestamp": datetime.utcnow()
        })

    return pd.DataFrame(audit_rows)

execution_audit_df = simulate_execution(final_execution_plan_df)

st.divider()
st.subheader("📜 Execution Audit Log")

st.dataframe(
    execution_audit_df,
    use_container_width=True,
    hide_index=True
)

st.caption("""
Simulated execution results for the planned actions.
In production, this data would be persisted for observability and rollback.
""")


