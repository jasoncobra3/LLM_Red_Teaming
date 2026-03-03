"""
Reusable model-selector widget for picking provider + model.
"""

from __future__ import annotations

import streamlit as st
from config.providers import PROVIDERS, get_configured_providers


def model_selector(
    label: str,
    key_prefix: str,
    allow_unconfigured: bool = True,
) -> tuple[str, str]:
    """
    Render a provider + model selector.

    Returns (provider_id, model_name).
    If allow_unconfigured is True, shows all providers; otherwise only configured ones.
    """
    providers = PROVIDERS if allow_unconfigured else get_configured_providers()
    if not providers:
        st.warning("No LLM providers configured. Add API keys in the Configure page.")
        return "", ""

    provider_names = {pid: info.display_name for pid, info in providers.items()}

    col1, col2 = st.columns([1, 2])

    with col1:
        selected_provider = st.selectbox(
            f"{label} Provider",
            list(provider_names.keys()),
            format_func=lambda x: provider_names[x],
            key=f"{key_prefix}_provider",
        )

    with col2:
        info = providers[selected_provider]
        model_options = info.default_models.copy()
        if info.supports_custom_model:
            model_options.append("✏️ Custom model…")

        selected_model = st.selectbox(
            f"{label} Model",
            model_options,
            key=f"{key_prefix}_model",
        )

        if selected_model == "✏️ Custom model…":
            selected_model = st.text_input(
                f"Enter custom model name",
                key=f"{key_prefix}_custom_model",
            )

    return selected_provider, selected_model
