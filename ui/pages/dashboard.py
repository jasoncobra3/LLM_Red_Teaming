"""
Dashboard page – overview of recent scans and platform health.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd

from database.db_manager import list_scan_runs
from config.providers import get_configured_providers
from ui.components.charts import score_gauge, attack_success_chart
from utils.helpers import severity_color, severity_label


def render():
    st.title("📊 Dashboard")
    st.caption("Overview of your LLM red-teaming activity")

    # ---- KPI Row ----
    scans = list_scan_runs(limit=100)
    configured = get_configured_providers()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Scans", len(scans))
    col2.metric("Providers Active", len(configured))

    completed = [s for s in scans if s.status == "completed"]
    avg_score = (
        sum(s.overall_score for s in completed) / len(completed) if completed else 0
    )
    col3.metric("Avg Score", f"{avg_score:.1f}%")

    total_vulns = sum(s.failed for s in completed)
    col4.metric("Vulns Found", total_vulns)

    st.divider()

    # ---- Latest Scan Gauge ----
    if completed:
        latest = completed[0]
        left, right = st.columns([1, 2])
        with left:
            score_gauge(latest.overall_score, title=f"Latest: {latest.name}")
        with right:
            st.subheader(f"Latest Scan: {latest.name}")
            st.markdown(f"**Status:** {latest.status}  |  **Score:** {latest.overall_score:.1f}%  |  {severity_color(latest.overall_score)} {severity_label(latest.overall_score)}")
            st.markdown(f"**Attacker:** `{latest.attacker_provider}/{latest.attacker_model}`")
            st.markdown(f"**Target:** `{latest.target_provider}/{latest.target_model}`")
            st.markdown(f"**Tests:** {latest.total_tests}  |  ✅ {latest.passed}  |  ❌ {latest.failed}")

        st.divider()

    # ---- Recent Scans Table ----
    st.subheader("Recent Scans")
    if scans:
        rows = []
        for s in scans[:20]:
            rows.append({
                "ID": s.id,
                "Name": s.name,
                "Status": s.status,
                "Score": f"{s.overall_score:.1f}%" if s.status == "completed" else "—",
                "Tests": s.total_tests,
                "Passed": s.passed,
                "Failed": s.failed,
                "Target": f"{s.target_provider}/{s.target_model}",
                "Created": s.created_at.strftime("%Y-%m-%d %H:%M") if s.created_at else "",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No scans yet. Head to **Attack Lab** to run your first red-team scan!")

    # ---- Quick-start tips ----
    with st.expander("🚀 Quick Start Guide"):
        st.markdown("""
        1. **Configure Models** – Add your API keys in the Configure page
        2. **Attack Lab** – Choose attacker & target models, select vulnerabilities and attacks, then launch
        3. **Results** – Review detailed findings for each scan
        4. **Reports** – Download professional PDF reports
        """)
