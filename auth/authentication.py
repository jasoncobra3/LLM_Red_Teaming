"""
Basic authentication for the Streamlit application.
Uses bcrypt for password hashing and Streamlit session state.
"""

from __future__ import annotations

import bcrypt
import streamlit as st

from config.settings import settings


def _hash_password(plain: str) -> str:
    """Hash a plain-text password with bcrypt."""
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def _verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False


def _get_password_hash() -> str:
    """Return the stored password hash, or auto-generate one for 'admin'."""
    stored = settings.AUTH_PASSWORD_HASH
    if stored:
        return stored
    # Fallback: default password is 'admin' (for first-time setup)
    return _hash_password("admin")


def login_form() -> bool:
    """
    Render a login form. Returns True if the user is authenticated.
    Sets st.session_state["authenticated"] = True on success.
    """
    if st.session_state.get("authenticated"):
        return True

    st.markdown(
        """
        <div style="display:flex;justify-content:center;margin-top:80px;">
            <div style="max-width:420px;width:100%;">
        """,
        unsafe_allow_html=True,
    )

    st.title("🔐 Login")
    st.caption("LLM Red Teaming Platform")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign In", use_container_width=True)

    if submitted:
        expected_user = settings.AUTH_USERNAME
        expected_hash = _get_password_hash()
        if username == expected_user and _verify_password(password, expected_hash):
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.rerun()
        else:
            st.error("Invalid username or password.")

    st.markdown("</div></div>", unsafe_allow_html=True)
    return False


def logout():
    """Clear session and force a rerun."""
    for key in ["authenticated", "username"]:
        st.session_state.pop(key, None)
    st.rerun()


def require_auth():
    """Gate: call at the top of every page to enforce login."""
    if not st.session_state.get("authenticated"):
        login_form()
        st.stop()
