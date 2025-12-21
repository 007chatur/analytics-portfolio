import streamlit as st
from pathlib import Path
import pandas as pd

st.set_page_config(page_title="Analytics Platform Portfolio", layout="wide")

st.title("👋 Hi, I'm a Senior Analytics Engineer")

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

st.markdown("""
This project demonstrates a **metadata-driven control plane** used to manage
analytics resources, access relationships, and execution governance at scale.

🔹 The architecture is **tool-agnostic by design**  
🔹 Looker is used as a **reference implementation**  
🔹 The same pattern applies to Snowflake, dbt, Tableau, Power BI, or internal tools
""")

from pathlib import Path
import pandas as pd

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
