"""
PDF Report Generator for Red Team scan results.
Uses fpdf2 to produce professional PDF reports.
"""

from __future__ import annotations

import datetime
import io
from pathlib import Path
from typing import Any, Dict, List

from fpdf import FPDF

from utils.helpers import severity_label, truncate


def _safe(text: str) -> str:
    """Replace characters unsupported by built-in Helvetica (latin-1 only)."""
    replacements = {
        "\u2014": "--",   # em-dash
        "\u2013": "-",    # en-dash
        "\u2018": "'",    # left single quote
        "\u2019": "'",    # right single quote
        "\u201c": '"',    # left double quote
        "\u201d": '"',    # right double quote
        "\u2026": "...",  # ellipsis
        "\u2022": "*",    # bullet
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    # Drop any remaining non-latin-1 chars
    return text.encode("latin-1", errors="replace").decode("latin-1")


def _break_long_words(text: str, max_word_len: int = 60) -> str:
    """Break very long words to prevent PDF rendering issues."""
    words = text.split()
    result = []
    for word in words:
        if len(word) > max_word_len:
            # Break long word into chunks
            for i in range(0, len(word), max_word_len):
                result.append(word[i:i + max_word_len])
        else:
            result.append(word)
    return " ".join(result)


class RedTeamReport(FPDF):
    """Custom FPDF subclass with header / footer branding."""

    def __init__(self, scan_name: str):
        super().__init__()
        self.scan_name = scan_name
        self.set_auto_page_break(auto=True, margin=20)
        self.set_left_margin(10)
        self.set_right_margin(10)

    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "LLM Red Teaming Platform -- Confidential", ln=True, align="R")
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def generate_pdf_report(
    scan_run: Any,
    results: List[Dict[str, Any]],
) -> bytes:
    """
    Generate a PDF report and return the raw bytes.

    Parameters
    ----------
    scan_run : ScanRun ORM object (or dict-like with same attributes)
    results  : list of result dicts from the scan
    """
    pdf = RedTeamReport(scan_name=scan_run.name)
    pdf.alias_nb_pages()
    pdf.add_page()

    # ---- Title ----
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 14, "Red Team Assessment Report", ln=True, align="C")
    pdf.ln(4)

    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 8, _safe(f"Scan: {scan_run.name}"), ln=True, align="C")
    pdf.cell(
        0, 8,
        _safe(f"Date: {getattr(scan_run, 'created_at', datetime.datetime.utcnow()).strftime('%Y-%m-%d %H:%M UTC')}"),
        ln=True, align="C",
    )
    pdf.ln(8)

    # ---- Executive Summary ----
    _section(pdf, "1. Executive Summary")
    total = getattr(scan_run, "total_tests", len(results))
    passed = getattr(scan_run, "passed", sum(1 for r in results if r.get("passed")))
    failed = getattr(scan_run, "failed", total - passed)
    score = getattr(scan_run, "overall_score", (passed / total * 100) if total else 0)

    summary_data = [
        ("Overall Score", f"{score:.1f}%"),
        ("Severity", severity_label(score)),
        ("Total Tests", str(total)),
        ("Passed (Safe)", str(passed)),
        ("Failed (Vulnerable)", str(failed)),
        ("Attacker Model", f"{getattr(scan_run, 'attacker_provider', 'N/A')} / {getattr(scan_run, 'attacker_model', 'N/A')}"),
        ("Target Model", f"{getattr(scan_run, 'target_provider', 'N/A')} / {getattr(scan_run, 'target_model', 'N/A')}"),
    ]
    _key_value_table(pdf, summary_data)
    pdf.ln(6)

    # ---- Vulnerability Breakdown ----
    _section(pdf, "2. Vulnerability Breakdown")
    vuln_stats = _aggregate_by_field(results, "vulnerability_type")
    if vuln_stats:
        _stats_table(pdf, "Vulnerability", vuln_stats)
    else:
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 8, "No vulnerability data available.", ln=True)
    pdf.ln(4)

    # ---- Attack Breakdown ----
    _section(pdf, "3. Attack Breakdown")
    atk_stats = _aggregate_by_field(results, "attack_type")
    if atk_stats:
        _stats_table(pdf, "Attack", atk_stats)
    else:
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 8, "No attack data available.", ln=True)
    pdf.ln(4)

    # ---- Detailed Results ----
    _section(pdf, "4. Detailed Results")
    for i, r in enumerate(results[:100], 1):  # limit to 100 for PDF size
        # Check if we need a new page (leave room for content)
        if pdf.get_y() > 240:
            pdf.add_page()
        
        pdf.set_font("Helvetica", "B", 10)
        status_str = "PASS" if r.get("passed") else "FAIL"
        pdf.set_text_color(0, 128, 0) if r.get("passed") else pdf.set_text_color(200, 0, 0)
        
        vuln_type = truncate(r.get('vulnerability_type', 'N/A'), 40)
        attack_type = truncate(r.get('attack_type', 'N/A'), 40)
        pdf.cell(0, 7, _safe(f"Test #{i} [{status_str}] - {vuln_type} / {attack_type}"), ln=True)
        pdf.set_text_color(30, 30, 30)

        pdf.set_font("Helvetica", "", 8)
        
        # NO TRUNCATION - show full content with word breaking for long words only
        prompt = _break_long_words(r.get("input_prompt", ""), 50)
        response = _break_long_words(r.get("target_response", ""), 50)
        
        # Parse reason JSON if possible, otherwise show full content
        reason_raw = r.get("reason", "")
        try:
            import json
            reason_obj = json.loads(reason_raw)
            reason = f"Score: {reason_obj.get('success_probability', 'N/A')}, Jailbreak: {reason_obj.get('jailbreak_achieved', 'N/A')}, Compliance: {reason_obj.get('compliance_level', 'N/A')}%"
        except:
            reason = _break_long_words(reason_raw, 50)

        # Display in order: Prompt, Response, Analysis with proper formatting
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(0, 5, _safe("Prompt:"), ln=True)
        pdf.set_font("Helvetica", "", 8)
        if prompt:
            try:
                pdf.multi_cell(0, 4, _safe(f"  {prompt}"))
            except Exception as e:
                try:
                    pdf.cell(0, 4, _safe("  [Content too complex to display]"), ln=True)
                except:
                    pass
        
        pdf.ln(1)
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(0, 5, _safe("Response:"), ln=True)
        pdf.set_font("Helvetica", "", 8)
        if response:
            try:
                pdf.multi_cell(0, 4, _safe(f"  {response}"))
            except Exception as e:
                try:
                    pdf.cell(0, 4, _safe("  [Content too complex to display]"), ln=True)
                except:
                    pass
        
        pdf.ln(1)
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(0, 5, _safe("Analysis:"), ln=True)
        pdf.set_font("Helvetica", "", 8)
        if reason:
            try:
                pdf.multi_cell(0, 4, _safe(f"  {reason}"))
            except Exception as e:
                try:
                    pdf.cell(0, 4, _safe("  [Content too complex to display]"), ln=True)
                except:
                    pass
        
        pdf.ln(3)

    # ---- Footer notes ----
    pdf.add_page()
    _section(pdf, "5. Methodology")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, (
        "This assessment was performed using the DeepTeam red-teaming framework. "
        "An attacker model generates adversarial prompts targeting known vulnerability "
        "categories. The target model's responses are evaluated by a judge model to "
        "determine whether the attack succeeded. A 'FAIL' indicates the target model "
        "was vulnerable to that specific attack vector."
    ))

    # Return bytes
    return pdf.output()


# -------------------------------------------------------------------
# Internal helpers
# -------------------------------------------------------------------

def _section(pdf: FPDF, title: str):
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(30, 60, 120)
    pdf.cell(0, 10, title, ln=True)
    pdf.set_draw_color(30, 60, 120)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)


def _key_value_table(pdf: FPDF, data: list[tuple[str, str]]):
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(30, 30, 30)
    for key, val in data:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(60, 7, _safe(key), border=0)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 7, _safe(val), border=0, ln=True)


def _stats_table(pdf: FPDF, label: str, stats: dict):
    # Header
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(230, 230, 240)
    pdf.cell(70, 7, label, border=1, fill=True)
    pdf.cell(25, 7, "Total", border=1, fill=True, align="C")
    pdf.cell(25, 7, "Passed", border=1, fill=True, align="C")
    pdf.cell(25, 7, "Failed", border=1, fill=True, align="C")
    pdf.cell(30, 7, "Pass Rate", border=1, fill=True, align="C")
    pdf.ln()

    pdf.set_font("Helvetica", "", 9)
    for name, s in stats.items():
        total = s["total"]
        p = s["passed"]
        f = s["failed"]
        rate = f"{(p / total * 100):.0f}%" if total else "N/A"
        pdf.cell(70, 7, _safe(truncate(name, 40)), border=1)
        pdf.cell(25, 7, str(total), border=1, align="C")
        pdf.cell(25, 7, str(p), border=1, align="C")
        pdf.cell(25, 7, str(f), border=1, align="C")
        pdf.cell(30, 7, rate, border=1, align="C")
        pdf.ln()


def _aggregate_by_field(results: list[dict], field: str) -> dict:
    agg: dict = {}
    for r in results:
        key = r.get(field, "unknown") or "unknown"
        if key not in agg:
            agg[key] = {"total": 0, "passed": 0, "failed": 0}
        agg[key]["total"] += 1
        if r.get("passed"):
            agg[key]["passed"] += 1
        else:
            agg[key]["failed"] += 1
    return agg
