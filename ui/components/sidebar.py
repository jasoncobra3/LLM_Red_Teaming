"""
Sidebar navigation component.
"""

from __future__ import annotations

import streamlit as st
from auth.authentication import logout


PAGES = {
    "Dashboard": "dashboard",
    "Configure Models": "configure",
    "Attack Lab": "attack_lab",
    "Scan History": "results",
    "Reports": "reports_page",
}


def render_sidebar():
    """Render the navigation sidebar. Returns the selected page key."""
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align:center;padding:10px 0 20px;">
                <h2 style="margin:0;">🛡️ Red Team</h2>
                <p style="margin:0;color:gray;font-size:0.85em;">LLM Security Testing</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.divider()

        page = st.radio(
            "Navigation",
            list(PAGES.keys()),
            label_visibility="collapsed",
        )

        st.divider()

        # Provider status
        from config.providers import get_configured_providers

        configured = get_configured_providers()
        st.markdown(f"**Providers configured:** {len(configured)}")
        for pid, info in configured.items():
            st.markdown(f"  ✅ {info.display_name}")

        st.divider()

        # User & logout
        username = st.session_state.get("username", "admin")
        st.caption(f"Logged in as **{username}**")
        if st.button("🚪 Logout", use_container_width=True):
            logout()

    return PAGES[page]
