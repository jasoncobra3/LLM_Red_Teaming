"""
Results page – browse scan history and drill into individual results.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd

from database.db_manager import list_scan_runs, get_scan_run, get_scan_results, delete_scan_run
from ui.components.charts import (
    score_gauge,
    vulnerability_pass_fail_chart,
    attack_success_chart,
    attack_type_heatmap,
)
from utils.helpers import severity_color, severity_label, truncate


def render():
    st.title("📜 Scan History & Results")

    scans = list_scan_runs(limit=100)
    if not scans:
        st.info("No scans found. Run a scan from the **Attack Lab** first.")
        return

    # ---- Scan Selector ----
    scan_options = {
        s.id: f"#{s.id} — {s.name} ({s.status}) — {s.created_at.strftime('%Y-%m-%d %H:%M') if s.created_at else ''}"
        for s in scans
    }
    selected_id = st.selectbox(
        "Select a scan",
        list(scan_options.keys()),
        format_func=lambda x: scan_options[x],
        key="result_scan_select",
    )

    scan = get_scan_run(selected_id)
    if not scan:
        st.error("Scan not found.")
        return

    # ---- Scan Summary ----
    st.divider()
    st.subheader(f"Scan: {scan.name}")

    mcol1, mcol2, mcol3, mcol4, mcol5 = st.columns(5)
    mcol1.metric("Status", scan.status.upper())
    mcol2.metric("Score", f"{scan.overall_score:.1f}%")
    mcol3.metric("Total Tests", scan.total_tests)
    mcol4.metric("Passed", scan.passed)
    mcol5.metric("Failed", scan.failed)

    st.markdown(
        f"**Severity:** {severity_color(scan.overall_score)} {severity_label(scan.overall_score)}  |  "
        f"**Attacker:** `{scan.attacker_provider}/{scan.attacker_model}`  |  "
        f"**Target:** `{scan.target_provider}/{scan.target_model}`"
    )

    if scan.target_purpose:
        st.markdown(f"**Target Purpose:** {scan.target_purpose}")

    # ---- Charts ----
    results_raw = get_scan_results(selected_id)
    results = [
        {
            "vulnerability_type": r.vulnerability_type,
            "attack_type": r.attack_type,
            "input_prompt": r.input_prompt,
            "target_response": r.target_response,
            "score": r.score,
            "passed": r.passed,
            "reason": r.reason,
            "risk_category": r.risk_category,
        }
        for r in results_raw
    ]

    if results:
        st.divider()

        chart1, chart2 = st.columns(2)
        with chart1:
            score_gauge(scan.overall_score)
        with chart2:
            attack_success_chart(results)

        vulnerability_pass_fail_chart(results)
        attack_type_heatmap(results)

        # ---- Detailed Results Table ----
        st.divider()
        st.subheader("Detailed Test Results")

        # Filters
        fcol1, fcol2, fcol3 = st.columns(3)
        with fcol1:
            vuln_filter = st.multiselect(
                "Filter by vulnerability",
                sorted(set(r["vulnerability_type"] for r in results)),
                key="vuln_filter",
            )
        with fcol2:
            atk_filter = st.multiselect(
                "Filter by attack",
                sorted(set(r["attack_type"] for r in results)),
                key="atk_filter",
            )
        with fcol3:
            status_filter = st.selectbox(
                "Status",
                ["All", "Passed", "Failed"],
                key="status_filter",
            )

        filtered = results
        if vuln_filter:
            filtered = [r for r in filtered if r["vulnerability_type"] in vuln_filter]
        if atk_filter:
            filtered = [r for r in filtered if r["attack_type"] in atk_filter]
        if status_filter == "Passed":
            filtered = [r for r in filtered if r["passed"]]
        elif status_filter == "Failed":
            filtered = [r for r in filtered if not r["passed"]]

        if filtered:
            df = pd.DataFrame(filtered)
            df["Status"] = df["passed"].map({True: "✅ Passed", False: "❌ Failed"})
            df["input_prompt"] = df["input_prompt"].apply(lambda x: truncate(x, 200))
            df["target_response"] = df["target_response"].apply(lambda x: truncate(x, 200))
            df["reason"] = df["reason"].apply(lambda x: truncate(x, 150))
            display_cols = ["Status", "vulnerability_type", "attack_type", "input_prompt", "target_response", "reason", "score"]
            st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
        else:
            st.info("No results match the current filters.")

        # ---- Expandable Detail View ----
        st.divider()
        st.subheader("Drill-Down View")
        for i, r in enumerate(filtered[:30]):
            status = "✅" if r["passed"] else "❌"
            with st.expander(f"{status} Test #{i+1} — {r['vulnerability_type']} / {r['attack_type']}"):
                st.markdown(f"**Score:** {r['score']:.2f}  |  **Status:** {'Passed' if r['passed'] else 'FAILED'}")
                if r.get("risk_category"):
                    st.markdown(f"**Risk Category:** {r['risk_category']}")
                st.markdown("**Input Prompt:**")
                st.code(r["input_prompt"] or "(empty)", language="text")
                st.markdown("**Target Response:**")
                st.code(r["target_response"] or "(empty)", language="text")
                if r.get("reason"):
                    st.markdown(f"**Evaluation Reason:** {r['reason']}")

    else:
        st.warning("No results available for this scan.")

    # ---- Delete scan ----
    st.divider()
    with st.expander("🗑️ Danger Zone"):
        st.warning("Deleting a scan is permanent and cannot be undone.")
        if st.button(f"Delete Scan #{scan.id}", type="primary"):
            delete_scan_run(scan.id)
            st.success("Scan deleted.")
            st.rerun()
