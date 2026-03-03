"""
Attack Lab page – configure and launch red-team scans.
"""

from __future__ import annotations

import threading
import streamlit as st

from ui.components.model_selector import model_selector
from core.attack_registry import (
    VULNERABILITIES,
    ATTACKS,
    FRAMEWORKS,
    get_vulnerability_categories,
    get_attack_categories,
)
from core.red_team_engine import run_red_team_scan
from database.db_manager import create_scan_run
from utils.helpers import ts_now


def render():
    st.title("⚔️ Attack Lab")
    st.caption("Configure and launch red-team scans against your LLM")

    # ================================================================
    # 1. Model Selection
    # ================================================================
    st.subheader("1️⃣ Select Models")

    left, right = st.columns(2)
    with left:
        st.markdown("**🗡️ Attacker (Simulator) Model**")
        st.caption("Generates adversarial prompts")
        atk_provider, atk_model = model_selector("Attacker", "atk")

    with right:
        st.markdown("**🎯 Target Model**")
        st.caption("The model being tested")
        tgt_provider, tgt_model = model_selector("Target", "tgt")

    target_purpose = st.text_area(
        "Target model purpose / system prompt (optional)",
        placeholder="e.g. 'A customer-support chatbot for a banking application'",
        key="target_purpose",
        height=80,
    )
    
    # Model selection guidance
    with st.expander("💡 Model Selection Tips"):
        st.markdown("""
        **Recommended Attacker Models:**
        - **OpenAI**: GPT-4, GPT-4 Turbo, GPT-3.5 Turbo (best for JSON generation)
        - **Anthropic**: Claude 3.5 Sonnet, Claude 3 Opus
        - **Azure OpenAI**: GPT-4, GPT-4o
        - **Groq**: Llama 3.1 70B, Mixtral 8x7B
        
        **Note**: The attacker model is also used for evaluation and must be capable of generating valid JSON output. 
        OpenAI and Azure OpenAI models work best due to their JSON mode support. If you encounter JSON errors, 
        try switching to GPT-4 or GPT-3.5-turbo as the attacker model.
        
        **Target Models**: Any model you want to test (can be the same or different from the attacker).
        """)

    st.divider()

    # ================================================================
    # 2. Vulnerability Selection
    # ================================================================
    st.subheader("2️⃣ Select Vulnerabilities to Test")

    vuln_categories = get_vulnerability_categories()
    selected_vulns: list[str] = []

    col_count = 3
    cols = st.columns(col_count)
    for idx, (cat, vulns) in enumerate(vuln_categories.items()):
        with cols[idx % col_count]:
            st.markdown(f"**{cat}**")
            for v in vulns:
                if st.checkbox(v.display_name, key=f"vuln_{v.id}", value=False):
                    selected_vulns.append(v.id)

    # Quick-select helpers
    qcol1, qcol2, qcol3 = st.columns(3)
    with qcol1:
        if st.button("Select All Vulnerabilities", use_container_width=True):
            for v in VULNERABILITIES:
                st.session_state[f"vuln_{v}"] = True
            st.rerun()
    with qcol2:
        if st.button("Clear All Vulnerabilities", use_container_width=True):
            for v in VULNERABILITIES:
                st.session_state[f"vuln_{v}"] = False
            st.rerun()
    with qcol3:
        if st.button("OWASP Top 10 Preset", use_container_width=True):
            owasp_vulns = [
                "prompt_injection", "pii_leakage", "misinformation",
                "toxicity", "bias", "sql_injection", "shell_injection",
                "ssrf", "excessive_agency", "robustness",
            ]
            for v in VULNERABILITIES:
                st.session_state[f"vuln_{v}"] = v in owasp_vulns
            st.rerun()

    st.divider()

    # ================================================================
    # 3. Attack Selection
    # ================================================================
    st.subheader("3️⃣ Select Attack Techniques")

    attack_categories = get_attack_categories()
    selected_attacks: list[str] = []

    for cat, attacks in attack_categories.items():
        label = "🔹 Single-Turn Attacks" if cat == "single_turn" else "🔸 Multi-Turn Attacks"
        st.markdown(f"**{label}**")
        atk_cols = st.columns(4)
        for idx, a in enumerate(attacks):
            with atk_cols[idx % 4]:
                if st.checkbox(a.display_name, key=f"atk_{a.id}", value=False):
                    selected_attacks.append(a.id)

    acol1, acol2 = st.columns(2)
    with acol1:
        if st.button("Select All Attacks", use_container_width=True):
            for a in ATTACKS:
                st.session_state[f"atk_{a}"] = True
            st.rerun()
    with acol2:
        if st.button("Clear All Attacks", use_container_width=True):
            for a in ATTACKS:
                st.session_state[f"atk_{a}"] = False
            st.rerun()

    st.divider()

    # ================================================================
    # 4. Compliance Framework (optional)
    # ================================================================
    st.subheader("4️⃣ Compliance Framework (Optional)")
    st.caption("When selected, the scan uses a predefined set of vulnerabilities from the framework.")

    framework_options = {"none": "No framework (use manual selection)"} | {
        fid: info.display_name for fid, info in FRAMEWORKS.items()
    }
    selected_framework = st.selectbox(
        "Framework",
        list(framework_options.keys()),
        format_func=lambda x: framework_options[x],
        key="framework_select",
    )
    if selected_framework == "none":
        selected_framework = None

    st.divider()

    # ================================================================
    # 5. Advanced Settings
    # ================================================================
    st.subheader("5️⃣ Advanced Settings")
    adv1, adv2 = st.columns(2)
    with adv1:
        attacks_per_vuln = st.slider(
            "Attacks per vulnerability type",
            min_value=1, max_value=20, value=5, step=1,
            key="attacks_per_vuln",
        )
    with adv2:
        scan_name = st.text_input(
            "Scan name",
            value=f"Scan-{ts_now().replace(':', '-')}",
            key="scan_name",
        )

    st.divider()

    # ================================================================
    # 6. Launch
    # ================================================================
    st.subheader("6️⃣ Launch Scan")

    # Validation
    ready = True
    if not atk_provider or not atk_model:
        st.warning("Please select an attacker model.")
        ready = False
    if not tgt_provider or not tgt_model:
        st.warning("Please select a target model.")
        ready = False
    if not selected_vulns and not selected_framework:
        st.warning("Select at least one vulnerability or a compliance framework.")
        ready = False

    # Summary before launch
    if ready:
        with st.expander("📋 Scan Configuration Summary", expanded=True):
            st.markdown(f"- **Name:** {scan_name}")
            st.markdown(f"- **Attacker:** `{atk_provider}/{atk_model}`")
            st.markdown(f"- **Target:** `{tgt_provider}/{tgt_model}`")
            st.markdown(f"- **Target Purpose:** {target_purpose or '(not specified)'}")
            st.markdown(f"- **Vulnerabilities:** {len(selected_vulns)} selected")
            st.markdown(f"- **Attacks:** {len(selected_attacks) or 'all (auto)'} selected")
            st.markdown(f"- **Framework:** {selected_framework or 'None'}")
            st.markdown(f"- **Attacks/vuln:** {attacks_per_vuln}")

    if st.button(
        "🚀 Launch Red Team Scan",
        type="primary",
        use_container_width=True,
        disabled=not ready,
    ):
        # Create DB record
        scan_run = create_scan_run(
            name=scan_name,
            attacker_provider=atk_provider,
            attacker_model=atk_model,
            target_provider=tgt_provider,
            target_model=tgt_model,
            target_purpose=target_purpose,
            vulnerabilities=selected_vulns,
            attacks=selected_attacks or None,
            framework=selected_framework,
            attacks_per_vuln=attacks_per_vuln,
        )

        st.session_state["active_scan_id"] = scan_run.id
        st.info(f"Scan **{scan_name}** (ID: {scan_run.id}) is launching…")

        # Run the scan (blocking for now – shows spinner)
        with st.spinner("Running red-team scan… This may take several minutes depending on model speed and number of tests."):
            summary = run_red_team_scan(
                scan_id=scan_run.id,
                attacker_provider=atk_provider,
                attacker_model=atk_model,
                target_provider=tgt_provider,
                target_model=tgt_model,
                target_purpose=target_purpose,
                vulnerability_ids=selected_vulns or None,
                attack_ids=selected_attacks or None,
                framework_id=selected_framework,
                attacks_per_vuln=attacks_per_vuln,
            )

        if summary["status"] == "completed":
            st.success(
                f"✅ Scan completed! Score: **{summary['score']:.1f}%** — "
                f"{summary['total_tests']} tests, {summary['passed']} passed, {summary['failed']} failed"
            )
            st.balloons()
        else:
            st.error(f"❌ Scan failed: {summary.get('error', 'Unknown error')}")
            with st.expander("Error details"):
                st.code(summary.get("traceback", ""))
