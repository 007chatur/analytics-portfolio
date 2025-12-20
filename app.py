import streamlit as st

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
