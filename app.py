"""
LLM Red Teaming Platform — Streamlit Application Entry Point
=============================================================

Launch with:
    streamlit run app.py
"""

from __future__ import annotations

# Fix for Windows async event loop cleanup issues
import sys
import asyncio
import warnings

if sys.platform == 'win32':
    # Use SelectorEventLoop instead of ProactorEventLoop on Windows
    # This prevents "Event loop is closed" errors during httpx cleanup
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    # Suppress async cleanup warnings
    warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*Event loop is closed.*")

import streamlit as st

# ---- Page Config (must be first Streamlit call) ----
st.set_page_config(
    page_title="LLM Red Teaming Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- Bootstrap DB ----
from database.db_manager import setup_database
setup_database()

# ---- Auth Gate ----
from auth.authentication import require_auth
require_auth()

# ---- Sidebar Navigation ----
from ui.components.sidebar import render_sidebar
page = render_sidebar()

# ---- Page Router ----
from ui.pages import dashboard, configure, attack_lab, results, reports_page

_PAGES = {
    "dashboard": dashboard,
    "configure": configure,
    "attack_lab": attack_lab,
    "results": results,
    "reports_page": reports_page,
}

module = _PAGES.get(page)
if module:
    module.render()
else:
    st.error(f"Unknown page: {page}")
