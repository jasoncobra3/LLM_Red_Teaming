"""
Reports page – generate and download PDF reports.
"""

from __future__ import annotations

import streamlit as st

from database.db_manager import list_scan_runs, get_scan_run, get_scan_results
from reports.pdf_generator import generate_pdf_report


def render():
    st.title("📄 Reports")
    st.caption("Generate and download professional PDF reports for completed scans")

    scans = list_scan_runs(limit=100)
    completed = [s for s in scans if s.status == "completed"]

    if not completed:
        st.info("No completed scans yet. Run a scan from the **Attack Lab** first.")
        return

    # ---- Scan selector ----
    scan_options = {
        s.id: f"#{s.id} — {s.name} — Score: {s.overall_score:.1f}% — {s.created_at.strftime('%Y-%m-%d %H:%M') if s.created_at else ''}"
        for s in completed
    }
    selected_id = st.selectbox(
        "Select a completed scan",
        list(scan_options.keys()),
        format_func=lambda x: scan_options[x],
        key="report_scan_select",
    )

    scan = get_scan_run(selected_id)
    if not scan:
        st.error("Scan not found.")
        return

    # ---- Scan info ----
    st.divider()
    col1, col2, col3 = st.columns(3)
    col1.metric("Score", f"{scan.overall_score:.1f}%")
    col2.metric("Tests", scan.total_tests)
    col3.metric("Failed", scan.failed)

    st.markdown(
        f"**Attacker:** `{scan.attacker_provider}/{scan.attacker_model}`  |  "
        f"**Target:** `{scan.target_provider}/{scan.target_model}`"
    )

    st.divider()

    # ---- Generate + Download ----
    if st.button("📥 Generate PDF Report", type="primary", use_container_width=True):
        with st.spinner("Generating report…"):
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

            pdf_bytes = generate_pdf_report(scan, results)

        filename = f"RedTeam_Report_{scan.name.replace(' ', '_')}_{scan.id}.pdf"
        st.download_button(
            label="⬇️ Download PDF Report",
            data=pdf_bytes,
            file_name=filename,
            mime="application/pdf",
            use_container_width=True,
        )
        st.success(f"Report generated! Click the button above to download **{filename}**.")

    # ---- Batch export ----
    st.divider()
    st.subheader("Batch Export")
    st.caption("Export results as CSV for further analysis")

    if st.button("📊 Export Results as CSV", use_container_width=True):
        import pandas as pd

        results_raw = get_scan_results(selected_id)
        if results_raw:
            rows = [
                {
                    "vulnerability_type": r.vulnerability_type,
                    "attack_type": r.attack_type,
                    "input_prompt": r.input_prompt,
                    "target_response": r.target_response,
                    "score": r.score,
                    "passed": r.passed,
                    "reason": r.reason,
                }
                for r in results_raw
            ]
            df = pd.DataFrame(rows)
            csv = df.to_csv(index=False)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"RedTeam_Results_{scan.id}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.warning("No results to export.")
