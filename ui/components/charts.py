"""
Reusable chart / visualisation helpers built with Plotly.
"""

from __future__ import annotations

from typing import Any, Dict, List

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st


def vulnerability_pass_fail_chart(results: List[Dict[str, Any]]):
    """Horizontal bar chart: pass/fail per vulnerability type."""
    if not results:
        st.info("No results to display.")
        return

    df = pd.DataFrame(results)
    if "vulnerability_type" not in df.columns:
        st.info("No vulnerability data.")
        return

    grouped = df.groupby("vulnerability_type")["passed"].agg(["sum", "count"]).reset_index()
    grouped.columns = ["Vulnerability", "Passed", "Total"]
    grouped["Failed"] = grouped["Total"] - grouped["Passed"]
    grouped = grouped.sort_values("Failed", ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(y=grouped["Vulnerability"], x=grouped["Passed"], name="Passed", orientation="h", marker_color="#2ecc71"))
    fig.add_trace(go.Bar(y=grouped["Vulnerability"], x=grouped["Failed"], name="Failed", orientation="h", marker_color="#e74c3c"))
    fig.update_layout(barmode="stack", title="Vulnerability Pass / Fail", height=max(300, len(grouped) * 35), margin=dict(l=200))
    st.plotly_chart(fig, use_container_width=True)


def attack_success_chart(results: List[Dict[str, Any]]):
    """Pie chart showing attack success vs. defence."""
    if not results:
        return

    df = pd.DataFrame(results)
    passed = df["passed"].sum()
    failed = len(df) - passed

    fig = px.pie(
        names=["Defended (Passed)", "Vulnerable (Failed)"],
        values=[passed, failed],
        color_discrete_sequence=["#2ecc71", "#e74c3c"],
        title="Overall Defence Rate",
    )
    fig.update_traces(textposition="inside", textinfo="percent+value")
    st.plotly_chart(fig, use_container_width=True)


def attack_type_heatmap(results: List[Dict[str, Any]]):
    """Heatmap of vulnerability × attack pass rate."""
    if not results:
        return

    df = pd.DataFrame(results)
    if "vulnerability_type" not in df.columns or "attack_type" not in df.columns:
        return

    pivot = df.pivot_table(
        index="vulnerability_type",
        columns="attack_type",
        values="passed",
        aggfunc="mean",
    ).fillna(0) * 100

    fig = px.imshow(
        pivot,
        color_continuous_scale="RdYlGn",
        title="Pass Rate Heatmap (Vulnerability × Attack)",
        labels=dict(x="Attack Type", y="Vulnerability", color="Pass %"),
        aspect="auto",
    )
    fig.update_layout(height=max(400, len(pivot) * 35))
    st.plotly_chart(fig, use_container_width=True)


def score_gauge(score: float, title: str = "Overall Score"):
    """Gauge meter for overall score."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=score,
            title={"text": title},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#3498db"},
                "steps": [
                    {"range": [0, 40], "color": "#fadbd8"},
                    {"range": [40, 60], "color": "#fdebd0"},
                    {"range": [60, 80], "color": "#fef9e7"},
                    {"range": [80, 100], "color": "#d5f5e3"},
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": 50,
                },
            },
        )
    )
    fig.update_layout(height=280, margin=dict(t=60, b=20))
    st.plotly_chart(fig, use_container_width=True)
