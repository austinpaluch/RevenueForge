import streamlit as st
import duckdb
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="RevenueForge", layout="wide", page_icon="📊")

st.title("RevenueForge — Executive Revenue Summary")
st.caption("SaaS Revenue Operations Intelligence Platform | Portfolio Project")

DB_PATH = Path(__file__).parent.parent / "data" / "processed" / "revenueforge.duckdb"
con = duckdb.connect(str(DB_PATH))

# === KPIs ===
st.subheader("Key Performance Indicators")

kpi = con.execute("""
    SELECT total_mrr, active_customers, mom_growth_pct 
    FROM mart_revenue_metrics ORDER BY month DESC LIMIT 1
""").df().iloc[0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Latest MRR", f"${kpi['total_mrr']:,.0f}")
col2.metric("Active Customers", f"{int(kpi['active_customers']):,}")
col3.metric("MoM Growth", f"{kpi['mom_growth_pct']:.1f}%", 
            delta_color="inverse" if kpi['mom_growth_pct'] < 0 else "normal")

win_rate = con.execute("""
    SELECT ROUND(100.0 * SUM(CASE WHEN is_closed_won THEN 1 ELSE 0 END) / 
           NULLIF(COUNT(CASE WHEN stage IN ('Closed Won','Closed Lost') THEN 1 END), 0), 1)
    FROM fact_pipeline
""").df().iloc[0, 0]
col4.metric("Overall Win Rate", f"{win_rate}%")

# === RFM Segmentation ===
st.subheader("Customer Segmentation (RFM)")

rfm = con.execute("""
    SELECT rfm_segment, COUNT(*) as count 
    FROM mart_rfm_segmentation 
    GROUP BY rfm_segment 
    ORDER BY count DESC
""").df()

col1, col2 = st.columns([2.3, 1])

with col1:
    st.bar_chart(rfm.set_index("rfm_segment"), use_container_width=True, height=300)

with col2:
    st.dataframe(rfm, hide_index=True, use_container_width=True)

# === Pipeline Performance ===
st.subheader("Sales Pipeline Performance")

pipeline = con.execute("SELECT * FROM mart_pipeline_performance").df()

pipeline_fmt = pipeline.copy()
pipeline_fmt["total_pipeline_value"] = pipeline_fmt["total_pipeline_value"].apply(lambda x: f"${x:,.0f}")
pipeline_fmt["avg_deal_size"] = pipeline_fmt["avg_deal_size"].apply(lambda x: f"${x:,.0f}")
pipeline_fmt["win_rate_pct"] = pipeline_fmt["win_rate_pct"].apply(lambda x: f"{x}%" if pd.notna(x) else "—")

st.dataframe(pipeline_fmt, hide_index=True, use_container_width=True)

# === Footer Note ===
st.caption("**Note:** This dashboard uses synthetic illustrative data generated for portfolio demonstration purposes.")

with st.expander("About this project & methodology"):
    st.markdown("""
    **RevenueForge** was built to demonstrate modern Business Intelligence capabilities relevant to remote BI Analyst roles.

    **Technologies used:**
    - DuckDB + dbt for data modeling and transformation
    - Advanced RFM customer segmentation
    - Accurate sales pipeline analytics (win rate calculated only on closed opportunities)
    - Clean, executive-ready presentation layer

    This project reflects real challenges I faced while generating over $2M in revenue using Salesforce and optimizing sales processes.
    """)