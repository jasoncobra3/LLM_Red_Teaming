"""
Configure page – manage API keys for LLM providers.
"""

from __future__ import annotations

import os
import streamlit as st

from config.providers import PROVIDERS
from config.settings import settings
from database.db_manager import save_api_key, get_api_key, list_api_keys


def render():
    st.title("⚙️ Configure Models")
    st.caption("Add or update API keys for your LLM providers")

    st.info(
        "API keys entered here are **saved in the local SQLite database**. "
        "For production use, store keys in environment variables or a secrets manager.",
        icon="🔑",
    )

    for pid, info in PROVIDERS.items():
        with st.expander(f"{'✅' if _is_configured(pid) else '⬜'} {info.display_name}", expanded=False):
            st.markdown(f"**Required env vars:** `{'`, `'.join(info.env_keys)}`")
            st.markdown(f"**Default models:** {', '.join(info.default_models[:4])}")

            # Show current status
            if _is_configured(pid):
                st.success("Configured via environment variable")
            else:
                stored = get_api_key(pid)
                if stored:
                    st.success("Configured via stored key")

            # Input form
            with st.form(f"form_{pid}"):
                fields = {}
                for key in info.env_keys:
                    current = getattr(settings, key, "") or ""
                    stored_rec = get_api_key(pid)
                    placeholder = "••••••••" if (current or (stored_rec and stored_rec.api_key)) else "Enter API key"
                    fields[key] = st.text_input(
                        key,
                        type="password",
                        placeholder=placeholder,
                        key=f"input_{pid}_{key}",
                    )

                # Extra config for Azure
                extra = {}
                if pid == "azure_openai":
                    extra["endpoint"] = st.text_input(
                        "Azure Endpoint URL",
                        value=settings.AZURE_OPENAI_ENDPOINT,
                        key=f"input_{pid}_endpoint",
                    )
                    extra["deployment"] = st.text_input(
                        "Deployment Name",
                        value=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                        key=f"input_{pid}_deployment",
                    )
                    extra["api_version"] = st.text_input(
                        "API Version",
                        value=settings.AZURE_OPENAI_API_VERSION,
                        key=f"input_{pid}_api_version",
                    )

                if pid == "aws_bedrock":
                    extra["region"] = st.text_input(
                        "AWS Region",
                        value=settings.AWS_DEFAULT_REGION,
                        key=f"input_{pid}_region",
                    )

                submitted = st.form_submit_button("💾 Save", use_container_width=True)

                if submitted:
                    # Save the primary key
                    primary_key = list(fields.values())[0]
                    if primary_key:
                        save_api_key(pid, primary_key, extra)
                        # Also set on the settings object for this session
                        for env_key, val in fields.items():
                            if val:
                                os.environ[env_key] = val
                                setattr(settings, env_key, val)
                        for ek, ev in extra.items():
                            env_name = f"{pid.upper()}_{ek.upper()}"
                            os.environ[env_name] = ev
                        st.success(f"✅ {info.display_name} key saved!")
                        st.rerun()
                    else:
                        st.warning("Please enter an API key.")

    st.divider()
    st.subheader("Provider Status Summary")
    status_data = []
    for pid, info in PROVIDERS.items():
        configured = _is_configured(pid) or get_api_key(pid) is not None
        status_data.append({
            "Provider": info.display_name,
            "Status": "✅ Configured" if configured else "❌ Not configured",
            "Models": ", ".join(info.default_models[:3]),
        })
    st.table(status_data)


def _is_configured(provider_id: str) -> bool:
    """Check if a provider has keys set in env vars."""
    info = PROVIDERS[provider_id]
    for key in info.env_keys:
        val = getattr(settings, key, "")
        if not val:
            return False
    return True
